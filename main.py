import os
import re
import json
import random
import logging
import requests
import time
from typing import Dict, List, Any

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# =========================================================
# 1. CONFIGURATION
# =========================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GUVI-Honeypot")

app = FastAPI(title="Agentic HoneyPot - HF Only (20s)")

SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
FINAL_REPORTED_SESSIONS = set()

# =========================================================
# 2. HUGGING FACE CLIENT (20s Timeout)
# =========================================================
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
# Using Phi-3 because it is the most reliable free model
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"

def query_hf_api(system_prompt, history, user_text):
    if not HF_TOKEN:
        logger.error("HF Token missing!")
        return None
    
    # Construct prompt
    prompt = f"<|system|>\n{system_prompt}<|end|>\n"
    for msg in history[-3:]: 
        role = "assistant" if msg.get("sender") == "bot" else "user"
        prompt += f"<|{role}|>\n{msg.get('text','')}<|end|>\n"
    prompt += f"<|user|>\n{user_text}<|end|>\n<|assistant|>"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 60,
            "return_full_text": False,
            "temperature": 0.7
        }
    }

    # ATTEMPT LOOP
    # We try twice. If the first one hangs for 20s, it fails.
    for attempt in range(2):
        try:
            logger.info(f"HF Request Attempt {attempt+1}...")
            r = requests.post(
                HF_API_URL, 
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json=payload,
                timeout=20  # <--- YOUR REQUESTED 20s TIMEOUT
            )
            
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and "generated_text" in data[0]:
                    return data[0]['generated_text'].strip()
            
            # If model is loading (503), wait 5s and try again
            elif r.status_code == 503:
                logger.warning("Model loading... waiting 5s")
                time.sleep(5)
                continue
            else:
                logger.error(f"HF Error {r.status_code}: {r.text}")
                
        except Exception as e:
            logger.warning(f"HF Timeout/Error: {e}")
            
    return None

# =========================================================
# 3. FAKE AI (The "Never Fail" Safety Net)
# =========================================================
# If HF is completely dead, these ensure you ALWAYS reply.
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
# 5. AGENTIC ENGAGEMENT
# =========================================================
def generate_reply(history, user_text):
    system_prompt = (
        "You are a naive, scared Indian bank customer named Ramesh. "
        "You trust the scammer but are confused. "
        "Keep asking questions to delay them. "
        "Reply in under 20 words."
    )

    # 1. Try Hugging Face (20s Timeout)
    reply = query_hf_api(system_prompt, history, user_text)
    if reply:
        return reply

    # 2. Fallback to Fake AI (Guaranteed Response if HF fails)
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
        sid = body.get("sessionId", "hf_session")
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