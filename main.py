import os
import re
import json
import random
import logging
import itertools
import requests
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

app = FastAPI(title="Agentic HoneyPot - Infinite Chat Edition")

SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
FINAL_REPORTED_SESSIONS = set()

# =========================================================
# 2. AI CLIENTS (GROQ + HF)
# =========================================================

# GROQ SETUP
groq_clients = []
try:
    from groq import Groq
    keys = [k.strip() for k in os.getenv("GROQ_KEYS", "").split(",") if k.strip()]
    for key in keys:
        groq_clients.append(Groq(api_key=key))
except Exception: pass

groq_pool = itertools.cycle(groq_clients) if groq_clients else None

# HUGGING FACE SETUP
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"

def query_hf(system_prompt, history, user_text):
    if not HF_TOKEN: return None
    
    prompt = f"<|system|>\n{system_prompt}<|end|>\n"
    for msg in history[-4:]:
        role = "assistant" if msg.get("sender") == "bot" else "user"
        prompt += f"<|{role}|>\n{msg.get('text','')}<|end|>\n"
    prompt += f"<|user|>\n{user_text}<|end|>\n<|assistant|>"

    try:
        r = requests.post(
            HF_API_URL, headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": prompt, "parameters": {"max_new_tokens": 60, "return_full_text": False}},
            timeout=15
        )
        if r.status_code == 200:
            return r.json()[0]['generated_text'].strip()
    except: pass
    return None

# =========================================================
# 3. INTELLIGENCE EXTRACTION
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
    return "Scammer detected via: " + ", ".join(reasons) if reasons else "Scam behavior detected"

# =========================================================
# 4. AGENTIC ENGAGEMENT (STRICTLY AI)
# =========================================================
def generate_reply(history, user_text):
    # UPDATED PROMPT: Forces infinite chat
    system_prompt = (
        "You are a confused, elderly Indian bank customer. "
        "You trust the scammer completely but you are bad at technology. "
        "Your goal is to keep them talking forever. "
        "Ask stupid questions. Pretend you are trying to pay. "
        "NEVER say goodbye. Reply in under 20 words."
    )

    # PRIORITY 1: GROQ
    if groq_pool:
        # Try up to 3 times with different keys to avoid failure
        for _ in range(3):
            try:
                client = next(groq_pool)
                messages = [{"role": "system", "content": system_prompt}]
                for h in history[-4:]:
                    role = "assistant" if h.get("sender") == "user" else "user" 
                    messages.append({"role": role, "content": str(h.get("text", ""))})
                messages.append({"role": "user", "content": user_text})

                r = client.chat.completions.create(
                    model="llama3-8b-8192", messages=messages, max_tokens=60, temperature=0.7
                )
                return r.choices[0].message.content.strip()
            except: continue

    # PRIORITY 2: HUGGING FACE
    hf_reply = query_hf(system_prompt, history, user_text)
    if hf_reply: return hf_reply

    # PRIORITY 3: FAILSAFE (Only if ALL AI fails)
    return "I am trying to do what you said, but my phone is very slow. Please wait."

# =========================================================
# 5. REPORTING
# =========================================================
def send_report(session_id, intel, turns):
    if session_id in FINAL_REPORTED_SESSIONS: return
    FINAL_REPORTED_SESSIONS.add(session_id)
    payload = {
        "sessionId": session_id, "scamDetected": True,
        "totalMessagesExchanged": turns, "extractedIntelligence": intel,
        "agentNotes": build_notes(intel)
    }
    try: requests.post(CALLBACK_URL, json=payload, timeout=10)
    except: pass

# =========================================================
# 6. MAIN ENDPOINT
# =========================================================
@app.post("/honey-pot-entry")
async def entry(request: Request, background: BackgroundTasks):
    try:
        raw = await request.body()
        body = json.loads(raw) if raw else {}
        if request.headers.get("x-api-key") != SECRET_API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid Key"})

        # Extraction
        msg = body.get("message", {})
        user_text = msg.get("text", "") if isinstance(msg, dict) else str(msg)
        sid = body.get("sessionId", "railway_session")
        history = body.get("conversationHistory", [])
        
        if not user_text: return {"status": "success", "reply": "I am here."}

        # Logic
        full_text = user_text + " " + " ".join([h.get("text", "") for h in history if isinstance(h, dict)])
        intel = extract_intel(full_text)
        
        # GENERATE REPLY (Strictly AI)
        reply = generate_reply(history, user_text)

        # Background Report
        turns = len(history) + 1
        if intel["scamDetected"]:
            background.add_task(send_report, sid, intel, turns)

        return {"status": "success", "reply": reply}

    except Exception:
        return {"status": "success", "reply": "My internet is acting up, please say again?"}

# RAILWAY PORT CONFIG
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)