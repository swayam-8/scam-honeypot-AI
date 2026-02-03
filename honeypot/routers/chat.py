from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from honeypot.AI import analyze_and_reply  
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# --- Data Models (Same as before) ---
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

# --- The Endpoint ---
@router.post("/chat")
async def chat_handler(payload: ScamRequest, x_api_key: str = Header(None)):
    
    # 1. Auth Check
    if x_api_key != os.environ.get("API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Extract Data
    user_msg = payload.message.text
    session_id = payload.sessionId
    
    print(f"Processing Session: {session_id}")

    # 3. Call the AI Brain (The logic is now separated!)
    ai_result = await analyze_and_reply(user_msg, payload.conversationHistory)

    # 4. Return the standardized response
    return {
        "status": "success",
        "reply": ai_result.get("reply", "...")
    }