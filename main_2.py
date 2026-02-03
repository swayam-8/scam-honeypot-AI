import os
import re
import json
import random
import logging
import requests
from typing import Dict, List, Any

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# NEW IMPORT FOR YOUR SPECIFIC CODE
from openai import OpenAI

# =========================================================
# 1. CONFIGURATION
# =========================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GUVI-Honeypot")

app = FastAPI(title="Agentic HoneyPot - GPT-OSS Edition")

SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
FINAL_REPORTED_SESSIONS = set()

# =========================================================
# 2. OPENAI CLIENT SETUP (USING YOUR EXACT CODE)
# =========================================================
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")

# Initialize Client exactly as you requested
client = None
if HF_TOKEN:
    try:
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=HF_TOKEN,
        )
        logger.info("✅ OpenAI Client for HF Router Initialized")
    except Exception as e:
        logger.error(f"Client Init Error: {e}")

# =========================================================
# 3. FAKE AI (Fallback)
# =========================================================
FAKE_AI_REPLIES = [
    "I am confused. Why do I need to do this urgently?",
    "My internet is very slow. Can you explain the steps again?",
    "I am scared to lose my money. Is this really the bank manager?",
    "Please wait, I am trying to find my glasses to read the OTP.",
    "I don't understand technology well. Will my account really be blocked?",
    "Can I call you? I prefer talking to someone."
]

# =========================================================
# 4. INTELLIGENCE EXTRACTION
# =========================================================
def extract_intel(text: str) -> Dict:
    intel = {
        "bankAccounts": list(set(re.findall(r"\b\d{9,18}\b", text))),
        "upiIds": list(set(re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text))),
        "phishingLinks": list(set(re.findall(r"https?://\S+", text))),
        "phoneNumbers": list(set(re.findall(r"(?:\+91[-\s]?)?[6-9]\d{9}", text))),
        "suspiciousKeywords": [k for k in ["urgent", "verify", "blocked", "otp", "kyc"] if k in text.lower()],
        "scamDetected": False
    }
    if any([intel["bankAccounts"], intel["upiIds"], intel["phishingLinks"], intel["suspiciousKeywords"]]):
        intel["scamDetected"] = True
    return intel

def build_notes(intel):
    reasons = [k for k, v in intel.items() if v and k != "scamDetected"]
    return "Scam detected via: " + ", ".join(reasons) if reasons else "Scam behavior detected"

# =========================================================
# 5. AGENTIC ENGAGEMENT (USING YOUR MODEL)
# =========================================================
def generate_reply(history, user_text):
    system_prompt = (
        "You are a naive, scared Indian bank customer named Ramesh. "
        "You trust the scammer but are confused. "
        "Keep asking questions to delay them. "
        "Reply in under 20 words."
    )

    if not client:
        return random.choice(FAKE_AI_REPLIES)

    # Convert history to OpenAI format
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-4:]:
        # Map our "sender" to OpenAI "role"
        role = "assistant" if msg.get("sender") == "bot" else "user"
        messages.append({"role": role, "content": str(msg.get("text", ""))})
    
    # Add current user message
    messages.append({"role": "user", "content": user_text})

    try:
        # YOUR EXACT MODEL CALL
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b:groq",
            messages=messages,
            max_tokens=60,
            temperature=0.7,
            timeout=20  # Keeping your safety timeout
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Model Error: {e}")
        return random.choice(FAKE_AI_REPLIES)

# =========================================================
# 6. REPORTING
# =========================================================
def send_report(session_id, intel, turns):
    if session_id in FINAL_REPORTED_SESSIONS: return
    FINAL_REPORTED_SESSIONS.add(session_id)
    payload = {
        "sessionId": session_id, "scamDetected": True,
        "totalMessagesExchanged": turns, "extractedIntelligence": intel,
        "agentNotes": build_notes(intel)
    }
    try: requests.post(CALLBACK_URL, json=payload, timeout=5)
    except: pass

# =========================================================
# 7. MAIN ENDPOINT
# =========================================================
@app.post("/honey-pot-entry")
async def entry(request: Request, background: BackgroundTasks):
    try:
        raw = await request.body()
        body = json.loads(raw) if raw else {}
        
        # Auth Check
        if request.headers.get("x-api-key") != SECRET_API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid Key"})

        # Extraction
        msg = body.get("message", {})
        user_text = msg.get("text", "") if isinstance(msg, dict) else str(msg)
        sid = body.get("sessionId", "gpt_oss_session")
        history = body.get("conversationHistory", [])
        
        if not user_text: return {"status": "success", "reply": "Hello?"}

        # Logic
        full_text = user_text + " " + " ".join([h.get("text", "") for h in history if isinstance(h, dict)])
        intel = extract_intel(full_text)
        
        # GENERATE REPLY
        reply = generate_reply(history, user_text)

        # Background Report
        turns = len(history) + 1
        if intel["scamDetected"]:
            background.add_task(send_report, sid, intel, turns)

        return {"status": "success", "reply": reply}

    except Exception:
        return {"status": "success", "reply": "I am trying to follow your instructions, please wait."}

# RAILWAY PORT CONFIG
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)