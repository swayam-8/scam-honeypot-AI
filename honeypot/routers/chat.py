from fastapi import APIRouter, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import httpx
import logging


from honeypot.AI import analyze_and_reply
from honeypot.utils import extract_intelligence
from honeypot.store import get_or_create_session, update_session, sessions

import os 
from dotenv import load_dotenv
load_dotenv()


router = APIRouter()
logger = logging.getLogger("uvicorn")

# --- Models ---
class MessageDetail(BaseModel):
    sender: str
    text: str
    timestamp: str

class Metadata(BaseModel):
    channel: Optional[str] = None

class ScamRequest(BaseModel):
    sessionId: str
    message: MessageDetail
    conversationHistory: List[MessageDetail]
    metadata: Optional[Metadata] = None

# --- Callback Function ---
async def send_final_report(payload: dict):
    """Sends the final intelligence to the Hackathon Judges"""
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"🚀 Sending Final Report for Session: {payload['sessionId']}")
            response = await client.post(url, json=payload, timeout=10.0)
            logger.info(f"✅ Report Status: {response.status_code} | Body: {response.text}")
        except Exception as e:
            logger.error(f"❌ Failed to report: {e}")

# --- Main Endpoint ---
@router.post("/chat")
async def chat_handler(payload: ScamRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    
    # 1. Auth
    if x_api_key != os.environ.get("API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_msg = payload.message.text
    session_id = payload.sessionId
    
    # 2. State & Intelligence
    get_or_create_session(session_id)
    new_intel = extract_intelligence(user_msg)
    current_state = update_session(session_id, new_intel)

    # 3. AI Processing
    ai_result = await analyze_and_reply(user_msg, payload.conversationHistory)
    
    # Increment count for our reply
    current_state["totalMessagesExchanged"] += 1
    
    # 4. CHECK: Is it time to end and report?
    # Logic: Report if > 8 messages OR if we found critical financial info
    has_critical_info = (len(current_state["extractedIntelligence"]["upiIds"]) > 0 or 
                         len(current_state["extractedIntelligence"]["bankAccounts"]) > 0)
    
    is_long_conversation = current_state["totalMessagesExchanged"] >= 8
    
    # ONLY send if we haven't sent it before
    if (has_critical_info or is_long_conversation) and not current_state["report_sent"]:
        
        final_payload = {
            "sessionId": session_id,
            "scamDetected": True, # We always assume True if the AI is engaged
            "totalMessagesExchanged": current_state["totalMessagesExchanged"],
            "extractedIntelligence": current_state["extractedIntelligence"],
            "agentNotes": "AI Agent successfully engaged scammer and extracted data."
        }
        
        # Use BackgroundTasks so we don't delay the reply to the scammer
        background_tasks.add_task(send_final_report, final_payload)
        
        # Mark as sent so we don't spam
        current_state["report_sent"] = True

    return {
        "status": "success",
        "reply": ai_result.get("reply", "...")
    }