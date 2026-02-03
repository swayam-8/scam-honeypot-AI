import os
import re
import json
import random
import logging
import itertools
import requests
import time
from typing import Dict, List, Any

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# =========================================================
# 1. SETUP & CONFIGURATION
# =========================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GUVI-Honeypot")

app = FastAPI(title="Agentic HoneyPot - Railway Edition")

# ⚠️ SECURITY: Get this from Railway Environment Variables
SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# Track reported sessions (Persists longer on Railway!)
FINAL_REPORTED_SESSIONS = set()

# =========================================================
# 2. AI CLIENT SETUP
# =========================================================
groq_clients = []
try:
    from groq import Groq
    keys = [k.strip() for k in os.getenv("GROQ_KEYS", "").split(",") if k.strip()]
    for key in keys:
        groq_clients.append(Groq(api_key=key))
except Exception as e:
    logger.warning(f"GROQ Setup Error: {e}")

groq_pool = itertools.cycle(groq_clients) if groq_clients else None

# =========================================================
# 3. ZOMBIE MODE (Fallback Persona)
# =========================================================
ZOMBIE_REPLIES = [
    "Why is my account being suspended? I am confused.",
    "Please tell me what to do next, I am scared.",
    "I don't understand technology well. Guide me.",
    "Will I lose my money? Please help.",
    "I am trying to open the app but it is slow."
]

# =========================================================
# 4. INTELLIGENCE EXTRACTION ENGINE
# =========================================================
def extract_intel(text: str) -> Dict:
    intel = {
        "bankAccounts": list(set(re.findall(r"\b\d{9,18}\b", text))),
        "upiIds": list(set(re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text))),
        "phishingLinks": list(set(re.findall(r"https?://\S+|www\.\S+", text))),
        "phoneNumbers": list(set(re.findall(r"(?:\+91[-\s]?)?[6-9]\d{9}", text))),
        "suspiciousKeywords": [],
        "scamDetected": False
    }

    keywords = ["urgent", "verify", "blocked", "suspended", "otp", "reward", "kyc", "expire"]
    intel["suspiciousKeywords"] = [k for k in keywords if k in text.lower()]

    if any([intel["bankAccounts"], intel["upiIds"], intel["phishingLinks"], intel["suspiciousKeywords"]]):
        intel["scamDetected"] = True

    return intel

def build_agent_notes(intel: Dict):
    reasons = []
    if intel["suspiciousKeywords"]: reasons.append("urgency/fear")
    if intel["upiIds"]: reasons.append("Requested UPI payment")
    if intel["bankAccounts"]: reasons.append("Shared bank details")
    if intel["phishingLinks"]: reasons.append("Shared malicious link")
    return "Scammer " + ", ".join(reasons) if reasons else "Scam intent detected via behavioral analysis"

# =========================================================
# 5. AGENTIC ENGAGEMENT
# =========================================================
def generate_reply(history, user_text):
    system_prompt = (
        "You are a naive, non-technical Indian bank customer. "
        "You are scared about your account being blocked. "
        "Believe the scammer implicitly. Ask simple questions. "
        "Delay the process by acting confused. "
        "Reply in under 20 words. NEVER admit you are an AI."
    )

    if groq_pool:
        try:
            client = next(groq_pool)
            messages = [{"role": "system", "content": system_prompt}]
            
            for h in history:
                if isinstance(h, dict):
                    role = "assistant" if h.get("sender") == "user" else "user" 
                    content = str(h.get("text", ""))
                    messages.append({"role": role, "content": content})
            
            messages.append({"role": "user", "content": user_text})

            r = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                max_tokens=60,
                temperature=0.6,
                timeout=12.0
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq failed: {e}")

    return random.choice(ZOMBIE_REPLIES)

# =========================================================
# 6. CALLBACK REPORTER
# =========================================================
def send_final_report(session_id, intel, turns):
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": turns,
        "extractedIntelligence": intel,
        "agentNotes": build_agent_notes(intel)
    }
    try:
        logger.info(f"Sending Report for {session_id}...")
        requests.post(CALLBACK_URL, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Callback Failed: {e}")

# =========================================================
# 7. API ENDPOINT
# =========================================================
@app.post("/honey-pot-entry")
async def honey_pot_entry(request: Request, background: BackgroundTasks):
    try:
        try:
            raw = await request.body()
            body = json.loads(raw) if raw else {}
        except:
            return {"status": "success", "reply": "Hello?"}

        if request.headers.get("x-api-key") != SECRET_API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

        session_id = body.get("sessionId", "unknown_session")
        message_obj = body.get("message", {})
        user_text = message_obj.get("text", "") if isinstance(message_obj, dict) else str(message_obj)
        history = body.get("conversationHistory", [])
        if not isinstance(history, list): history = []

        if not user_text:
            return {"status": "success", "reply": "I am listening."}

        full_context = user_text + " " + " ".join([h.get("text", "") for h in history if isinstance(h, dict)])
        intel = extract_intel(full_context)
        reply = generate_reply(history, user_text)

        turns = len(history) + 1
        if intel["scamDetected"]:
             background.add_task(send_final_report, session_id, intel, turns)

        return {"status": "success", "reply": reply}

    except Exception:
        return {"status": "success", "reply": "My internet is slow, please wait."}

# =========================================================
# 8. RAILWAY START CONFIGURATION (CRITICAL)
# =========================================================
if __name__ == "__main__":
    # Railway assigns a dynamic PORT variable. We MUST use it.
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)