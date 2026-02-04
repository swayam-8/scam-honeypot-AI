import os
import re
import json
import logging
from typing import Optional, Dict, List
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables with defaults
API_KEY = os.getenv("API_KEY", "default_secret_key_change_me")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

app = FastAPI(title="Scam Honeypot AI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Scam Honeypot AI Service Starting...")
    logger.info(f"API Key configured: {bool(API_KEY)}")
    logger.info(f"Debug mode: {DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Scam Honeypot AI Service Shutting Down...")

def scam_intent_detected(text: str) -> bool:
    """Detect scam intent based on keywords."""
    if not text or not isinstance(text, str):
        return False
    scam_keywords = [
        "verify", "account blocked", "urgent", "suspend", "upi", "bank account", 
        "phishing", "payment", "otp", "link", "confirm", "authenticate", "validate",
        "compromise", "freeze", "deactivate", "expired"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in scam_keywords)

def extract_intelligence(messages: List[Dict]) -> Dict:
    """Extract intelligence from messages."""
    bank_accounts = []
    upi_ids = []
    phishing_links = []
    phone_numbers = []
    suspicious_keywords = []

    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    bank_pattern = r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
    link_pattern = r"https?://[^\s]+"
    phone_pattern = r"\+?91[\d\s]{10}|\+?1[\d\s]{10}"
    keywords = ["urgent", "verify", "account blocked", "otp", "payment", "suspend", "confirm", "immediate", "action required"]

    for msg in messages:
        text = msg.get("text", "")
        if not isinstance(text, str):
            continue
        
        try:
            bank_accounts.extend(re.findall(bank_pattern, text))
            upi_ids.extend(re.findall(upi_pattern, text))
            phishing_links.extend(re.findall(link_pattern, text))
            phone_numbers.extend(re.findall(phone_pattern, text))
            
            for kw in keywords:
                if kw in text.lower():
                    suspicious_keywords.append(kw)
        except Exception as e:
            logger.error(f"Error extracting intelligence: {e}")

    return {
        "bankAccounts": list(set(bank_accounts))[:5],
        "upiIds": list(set(upi_ids))[:5],
        "phishingLinks": list(set(phishing_links))[:5],
        "phoneNumbers": list(set(phone_numbers))[:5],
        "suspiciousKeywords": list(set(suspicious_keywords))[:10]
    }

def agent_reply(message: str, history: List[Dict]) -> str:
    """Generate agent reply."""
    if not message or not isinstance(message, str):
        return "Could you please repeat that?"
    
    message_lower = message.lower()
    
    if "account" in message_lower and ("block" in message_lower or "suspend" in message_lower):
        return "Why is my account being suspended? Can you provide more details?"
    elif "upi" in message_lower:
        return "Can you explain why you need my UPI ID?"
    elif "verify" in message_lower or "confirm" in message_lower:
        return "How do I verify my account safely?"
    elif "otp" in message_lower:
        return "Why do you need my OTP? I thought that was confidential."
    elif "link" in message_lower or "click" in message_lower:
        return "I'm hesitant to click links from unknown sources. Can you verify your identity first?"
    elif "password" in message_lower or "pin" in message_lower:
        return "I will never share my password or PIN with anyone."
    else:
        return "Can you provide more details about what you're saying?"

def send_final_result(session_id: str, scam_detected: bool, total_messages: int, 
                      intelligence: Dict, agent_notes: str) -> bool:
    """Send final result to GUVI endpoint."""
    if not session_id:
        logger.error("Invalid session_id for final result")
        return False
    
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": agent_notes
    }
    try:
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=10
        )
        logger.info(f"✅ Final result sent: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.Timeout:
        logger.error("Timeout sending final result")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error sending final result: {e}")
        return False

@app.head("/")
async def head_root():
    return Response(status_code=200)

@app.get("/")
async def root():
    return {"status": "ok", "service": "Scam Honeypot AI", "version": "1.0"}

@app.head("/honeypot")
async def head_honeypot():
    return Response(status_code=200)

@app.post("/honeypot")
async def honeypot_endpoint(
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    """Main honeypot endpoint."""
    if not x_api_key or x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")

    try:
        data = await request.json()
    except json.JSONDecodeError as e:
        logger.error(f"JSON Parse Error: {e}")
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Invalid JSON format",
            "detail": str(e)
        })
    except Exception as e:
        logger.error(f"Request parsing error: {e}")
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Failed to parse request"
        })

    # Validate required fields
    if not data.get("sessionId") or not data.get("message"):
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Missing sessionId or message"
        })

    session_id = str(data.get("sessionId", "")).strip()
    message = data.get("message", {})
    conversation_history = data.get("conversationHistory", []) or []

    # Validate message structure
    if not isinstance(message, dict) or not message.get("text"):
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Invalid message structure"
        })

    try:
        all_messages = conversation_history + [message]
        scam_detected = scam_intent_detected(message.get("text", ""))
        reply = agent_reply(message.get("text", ""), conversation_history)
        intelligence = extract_intelligence(all_messages)

        agent_notes = "Scammer used urgency, account threats, and payment redirection tactics" if scam_detected else "No scam detected"

        response_json = {
            "status": "success",
            "reply": reply,
            "scamDetected": scam_detected
        }

        logger.info(f"🔍 Session {session_id}: Scam={scam_detected}, Messages={len(all_messages)}")

        # Send final result if scam detected and enough engagement
        if scam_detected and len(all_messages) >= 3:
            send_final_result(
                session_id=session_id,
                scam_detected=True,
                total_messages=len(all_messages),
                intelligence=intelligence,
                agent_notes=agent_notes
            )

        return JSONResponse(content=response_json, status_code=200)

    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Internal server error"
        })

@app.post("/chat")
async def chat_endpoint(request: Request, x_api_key: Optional[str] = Header(None)):
    """Alias endpoint for /honeypot."""
    return await honeypot_endpoint(request, x_api_key)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Scam Honeypot AI", "timestamp": __import__("time").time()}
