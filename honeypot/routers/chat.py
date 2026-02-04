import os
import json
import logging
import time
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from fastapi import APIRouter, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx

from honeypot.AI import analyze_and_reply
from honeypot.utils import extract_intelligence
from honeypot.store import (
    get_or_create_session,
    update_session,
    add_message_to_session,
    should_send_report,
    mark_report_sent
)

load_dotenv()
router = APIRouter()
logger = logging.getLogger("uvicorn")

# ==================== DATA MODELS ====================

class MessageDetail(BaseModel):
    sender: Optional[str] = None
    text: Optional[str] = None
    timestamp: Optional[int] = None

class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class ScamRequest(BaseModel):
    sessionId: Optional[str] = None
    message: Optional[MessageDetail] = None
    conversationHistory: Optional[List[MessageDetail]] = []
    metadata: Optional[Metadata] = None

class ScamResponse(BaseModel):
    status: str
    reply: str
    is_scam: Optional[bool] = None
    confidence: Optional[float] = None

# ==================== HELPER FUNCTIONS ====================

async def send_final_report(payload: Dict[str, Any]):
    """
    Send final intelligence report to evaluation endpoint.
    """
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            logger.info(f"📤 Sending report for session: {payload.get('sessionId')}")
            response = await client.post(url, json=payload)
            logger.info(f"✅ Report sent. Status: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Report failed: {str(e)}")
            return False

# ==================== ENDPOINTS ====================

@router.post("/chat", response_model=ScamResponse)
async def chat_handler(
    payload: ScamRequest,
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(None)
):
    """
    Main chat endpoint for processing scam messages.
    
    - Validates API key if configured
    - Extracts intelligence from messages
    - Generates AI responses
    - Sends reports when criteria met
    """
    
    logger.info(f"📥 Incoming request: {payload}")
    
    # API Key validation
    valid_key = os.environ.get("API_KEY")
    if valid_key and x_api_key != valid_key:
        logger.warning(f"❌ Authentication failed")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Handle ping/empty requests
    if not payload.message or not payload.message.text:
        logger.info("✅ Ping request - HoneyPot active")
        return ScamResponse(
            status="success",
            reply="HoneyPot is active and listening"
        )
    
    # Extract session info
    user_msg = payload.message.text.strip()
    session_id = payload.sessionId or f"session_{int(time.time())}"
    channel = payload.metadata.channel if payload.metadata else "unknown"
    
    logger.info(f"🔍 Processing message in session: {session_id}")
    
    # Get/create session
    session = get_or_create_session(session_id)
    
    # Extract intelligence
    intel = extract_intelligence(user_msg)
    update_session(session_id, intel)
    
    # Build conversation history
    history = []
    if payload.conversationHistory:
        history = [
            {
                "sender": msg.sender or "unknown",
                "text": msg.text or ""
            }
            for msg in payload.conversationHistory
        ]
    
    # Add current message
    add_message_to_session(session_id, {
        "sender": "scammer",
        "text": user_msg,
        "timestamp": int(time.time() * 1000)
    })
    
    # Generate AI response
    try:
        ai_result = await analyze_and_reply(user_msg, history)
    except Exception as e:
        logger.error(f"⚠️ AI error: {str(e)}")
        ai_result = {
            "is_scam": True,
            "reply": "Can you explain that again?",
            "confidence": 0.5
        }
    
    # Update session
    session["totalMessagesExchanged"] += 1
    
    # Add AI response to history
    add_message_to_session(session_id, {
        "sender": "agent",
        "text": ai_result.get("reply", "I don't understand"),
        "timestamp": int(time.time() * 1000)
    })
    
    logger.info(f"📤 AI Response: {ai_result.get('reply')}")
    
    # Check if report should be sent
    if should_send_report(session_id) and not session.get("report_sent"):
        final_payload = {
            "sessionId": str(session_id),
            "scamDetected": True,
            "totalMessagesExchanged": session["totalMessagesExchanged"],
            "extractedIntelligence": {
                "bankAccounts": session["extractedIntelligence"].get("bankAccounts", []),
                "upiIds": session["extractedIntelligence"].get("upiIds", []),
                "phishingLinks": session["extractedIntelligence"].get("phishingLinks", []),
                "phoneNumbers": session["extractedIntelligence"].get("phoneNumbers", []),
                "suspiciousKeywords": session["extractedIntelligence"].get("suspiciousKeywords", [])
            },
            "agentNotes": f"Scammer engaged in {session['totalMessagesExchanged']} messages on {channel}. Used social engineering tactics."
        }
        
        logger.info(f"📋 Scheduling report for session: {session_id}")
        background_tasks.add_task(send_final_report, final_payload)
        mark_report_sent(session_id)
    
    return ScamResponse(
        status="success",
        reply=ai_result.get("reply"),
        is_scam=ai_result.get("is_scam"),
        confidence=ai_result.get("confidence")
    )
