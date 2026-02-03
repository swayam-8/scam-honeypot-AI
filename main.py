import os
import re
import json
import random
import logging
import itertools
import requests
from typing import Dict

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# =========================================================
# 1. SETUP
# =========================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GUVI-Honeypot")

app = FastAPI(title="Agentic HoneyPot - Problem 2")

SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

FINAL_REPORTED_SESSIONS = set()

# =========================================================
# 2. GROQ SETUP
# =========================================================
groq_clients = []
try:
    from groq import Groq
    keys = [k.strip() for k in os.getenv("GROQ_KEYS", "").split(",") if k.strip()]
    for key in keys:
        groq_clients.append(Groq(api_key=key))
except Exception as e:
    logger.warning(f"GROQ not available: {e}")

groq_pool = itertools.cycle(groq_clients) if groq_clients else None

# =========================================================
# 3. HUGGINGFACE SETUP
# =========================================================
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"

def query_hf(system_prompt, history, user_text):
    if not HF_TOKEN:
        return None

    prompt = f"<|system|>\n{system_prompt}<|end|>\n"
    for msg in history[-4:]:
        role = "assistant" if msg.get("sender") == "user" else "user"
        prompt += f"<|{role}|>\n{msg.get('text','')}<|end|>\n"

    prompt += f"<|user|>\n{user_text}<|end|>\n<|assistant|>"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 60,
            "temperature": 0.5,
            "return_full_text": False
        }
    }

    try:
        r = requests.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json=payload,
            timeout=12
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                logger.info("✅ HuggingFace model used")
                return data[0]["generated_text"].strip()
    except Exception as e:
        logger.warning(f"HF failed: {e}")

    return None

# =========================================================
# 4. FALLBACK RESPONSES
# =========================================================
FALLBACK_REPLIES = [
    "Why is this happening suddenly?",
    "Can you explain the issue clearly?",
    "I am not understanding this properly.",
    "Is there any official confirmation?",
    "Please guide me step by step."
]

# =========================================================
# 5. INTELLIGENCE EXTRACTION
# =========================================================
def extract_intel(text: str) -> Dict:
    intel = {
        "bankAccounts": list(set(re.findall(r"\b\d{9,18}\b", text))),
        "upiIds": list(set(re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text))),
        "phishingLinks": list(set(re.findall(r"https?://\S+", text))),
        "phoneNumbers": list(set(re.findall(r"(?:\+91[-\s]?)?[6-9]\d{9}", text))),
        "suspiciousKeywords": [],
        "scamDetected": False
    }

    keywords = ["urgent", "verify", "blocked", "suspended", "otp", "reward", "kyc"]
    intel["suspiciousKeywords"] = [k for k in keywords if k in text.lower()]

    if any([
        intel["bankAccounts"],
        intel["upiIds"],
        intel["phishingLinks"],
        intel["phoneNumbers"],
        intel["suspiciousKeywords"]
    ]):
        intel["scamDetected"] = True

    return intel

def build_agent_notes(intel: Dict):
    reasons = []
    if intel["suspiciousKeywords"]: reasons.append("urgency / verification pressure")
    if intel["upiIds"]: reasons.append("UPI requested")
    if intel["bankAccounts"]: reasons.append("bank details requested")
    if intel["phishingLinks"]: reasons.append("malicious link shared")
    if intel["phoneNumbers"]: reasons.append("phone number used")

    return "Scammer behavior: " + ", ".join(reasons) if reasons else "Suspicious behavior detected"

# =========================================================
# 6. RESPONSE GENERATION (GENERAL PERSONA)
# =========================================================
def generate_reply(history, user_text):
    system_prompt = (
        "You are a normal Indian bank customer. "
        "You are confused but polite. "
        "Ask questions, delay sharing details. "
        "Never reveal scam detection. "
        "Reply under 25 words."
    )

    # 1️⃣ GROQ
    if groq_pool:
        try:
            client = next(groq_pool)
            messages = [{"role": "system", "content": system_prompt}]
            for h in history[-4:]:
                role = "assistant" if h.get("sender") == "user" else "user"
                messages.append({"role": role, "content": h.get("text", "")})
            messages.append({"role": "user", "content": user_text})

            r = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                max_tokens=60,
                temperature=0.5
            )
            logger.info("✅ GROQ model used")
            return r.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"GROQ failed: {e}")

    # 2️⃣ HF
    hf = query_hf(system_prompt, history, user_text)
    if hf:
        return hf

    # 3️⃣ Fallback
    logger.warning("⚠️ Static fallback used")
    return random.choice(FALLBACK_REPLIES)

# =========================================================
# 7. FINAL CALLBACK
# =========================================================
def send_final_report(session_id, intel, turns):
    if session_id in FINAL_REPORTED_SESSIONS:
        return

    FINAL_REPORTED_SESSIONS.add(session_id)

    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": turns,
        "extractedIntelligence": {
            "bankAccounts": intel["bankAccounts"],
            "upiIds": intel["upiIds"],
            "phishingLinks": intel["phishingLinks"],
            "phoneNumbers": intel["phoneNumbers"],
            "suspiciousKeywords": intel["suspiciousKeywords"]
        },
        "agentNotes": build_agent_notes(intel)
    }

    try:
        requests.post(CALLBACK_URL, json=payload, timeout=12)
        logger.info("📤 Final intelligence sent to GUVI")
    except Exception as e:
        logger.error(f"Callback failed: {e}")

# =========================================================
# 8. MAIN ENDPOINT
# =========================================================
@app.post("/honey-pot-entry")
async def honeypot(request: Request, background: BackgroundTasks):

    raw = await request.body()
    if not raw:
        return {"status": "success", "reply": "Hello, how can I help?"}

    try:
        body = json.loads(raw)
    except Exception:
        body = {}

    api_key = request.headers.get("x-api-key")
    if api_key != SECRET_API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

    message = body.get("message", {})
    session_id = body.get("sessionId", "unknown-session")
    history = body.get("conversationHistory", [])

    user_text = message.get("text", "") if isinstance(message, dict) else str(message)
    if not user_text:
        return {"status": "success", "reply": "Can you repeat that?"}

    combined = user_text + " " + " ".join(
        h.get("text", "") for h in history if isinstance(h, dict)
    )

    intel = extract_intel(combined)
    reply = generate_reply(history, user_text)

    turns = len(history) + 1
    if intel["scamDetected"] and (
        turns >= 6 or intel["upiIds"] or intel["bankAccounts"] or intel["phishingLinks"]
    ):
        background.add_task(send_final_report, session_id, intel, turns)

    return {
        "status": "success",
        "reply": reply
    }

# =========================================================
# 9. HEALTH
# =========================================================
@app.get("/health")
async def health():
    return {"status": "healthy"}
