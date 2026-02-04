import os 
from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
import httpx
import logging
import json

# Import your modules
from honeypot.AI import analyze_and_reply
from honeypot.utils import extract_intelligence
from honeypot.store import (
    get_or_create_session, 
    update_session, 
    add_message_to_session,
    should_send_report,
    mark_report_sent
)

router = APIRouter()
logger = logging.getLogger("uvicorn")

# --- DATA MODELS ---
class MessageDetail(BaseModel):
    sender: Optional[str] = None
    text: Optional[str] = None
    timestamp: Optional[Union[str, int]] = None  

class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class ScamRequest(BaseModel):
    sessionId: Optional[str] = None
    message: Optional[MessageDetail] = None
    conversationHistory: Optional[List[MessageDetail]] = [] 
    metadata: Optional[Metadata] = None

# --- Callback Function ---
async def send_final_report(payload: dict):
    """
    Sends final scam intelligence to GUVI evaluation endpoint.
    This is mandatory for scoring.
    """
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"🚀 Sending Final Report for Session: {payload['sessionId']}")
            logger.info(f"📊 Payload: {json.dumps(payload, indent=2)}")
            response = await client.post(url, json=payload, timeout=10.0)
            logger.info(f"✅ Report Status: {response.status_code}")
            logger.info(f"📝 Response: {response.text}")
        except Exception as e:
            logger.error(f"❌ Failed to send report: {e}")

# --- 2. INTELLIGENT ENDPOINT ---
@router.post("/chat")
async def chat_handler(
    payload: ScamRequest, 
    background_tasks: BackgroundTasks, 
    x_api_key: str = Header(None)
):
    """
    Main endpoint for processing scam messages.
    
    Accepts incoming messages from potential scammers, detects scam intent,
    and generates human-like responses to extract intelligence.
    """
    
    # Debug: Print incoming request
    logger.info(f"📥 Incoming Request: {payload.model_dump_json(indent=2)}")

    # 1. Authentication Check
    valid_key = os.environ.get("API_KEY")
    if valid_key and x_api_key != valid_key:
        logger.warning(f"❌ Auth Failed. Received: {x_api_key} | Expected: {valid_key}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Handle Empty/Ping Requests
    if not payload.message or not payload.message.text:
        logger.info("✅ Ping detected - HoneyPot Active")
        return {
            "status": "success",
            "reply": "Connection Successful. HoneyPot is active."
        }

    # --- SCAM PROCESSING LOGIC ---
    
    user_msg = payload.message.text.strip()
    session_id = payload.sessionId or "unknown_session"
    channel = payload.metadata.channel if payload.metadata else "unknown"
    language = payload.metadata.language if payload.metadata else "English"
    
    logger.info(f"🔍 Processing Session: {session_id} | Message: {user_msg}")

    # Create/Get session state
    session_state = get_or_create_session(session_id)
    
    # Extract intelligence from current message
    new_intel = extract_intelligence(user_msg)
    
    # Update session with new intelligence
    update_session(session_id, new_intel)
    
    # Build conversation history for context
    history = []
    if payload.conversationHistory:
        history = [
            {
                "sender": msg.sender or "unknown",
                "text": msg.text or "",
                "timestamp": msg.timestamp
            }
            for msg in payload.conversationHistory
        ]
    
    # Add current message to conversation history
    add_message_to_session(session_id, {
        "sender": "scammer",
        "text": user_msg,
        "timestamp": payload.message.timestamp
    })
    
    # AI Analysis & Response Generation
    try:
        ai_result = await analyze_and_reply(user_msg, history)
    except Exception as e:
        logger.error(f"⚠️ AI Error: {e}")
        ai_result = {
            "is_scam": True,
            "reply": "I don't understand. Can you explain?",
            "confidence": 0.5
        }
    
    # Update message count (only count incoming scammer messages)
    session_state["totalMessagesExchanged"] += 1
    
    # Add AI response to conversation history
    agent_reply = ai_result.get("reply", "I'm confused.")
    add_message_to_session(session_id, {
        "sender": "user",
        "text": agent_reply,
        "timestamp": int(__import__("time").time() * 1000)
    })
    
    logger.info(f"📤 AI Response: {agent_reply}")
    logger.info(f"📊 Current State: {session_state}")
    
    # Check if we should send the final report
    should_report = should_send_report(session_id)
    
    if should_report and not session_state.get("report_sent", False):
        # Ensure all data is JSON serializable
        extracted_intel = session_state["extractedIntelligence"].copy()
        for key in extracted_intel:
            extracted_intel[key] = [str(item) for item in extracted_intel[key]]
        
        final_payload = {
            "sessionId": str(session_id),
            "scamDetected": True,
            "totalMessagesExchanged": int(session_state["totalMessagesExchanged"]),
            "extractedIntelligence": extracted_intel,
            "agentNotes": f"Scammer engaged in {session_state['totalMessagesExchanged']} messages on {channel} ({language}). Used urgency and authority tactics."
        }
        logger.info(f"📋 Scheduling Report Send for Session: {session_id}")
        background_tasks.add_task(send_final_report, final_payload)
        mark_report_sent(session_id)

    return {
        "status": "success",
        "reply": agent_reply
    }