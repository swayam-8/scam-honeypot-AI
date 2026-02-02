import os
import re
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
logger = logging.getLogger("GUVI-HoneyPot")

app = FastAPI(title="Agentic HoneyPot - Problem 2")

SECRET_API_KEY = os.getenv("SECRET_API_KEY")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

FINAL_REPORTED_SESSIONS = set()

# =========================================================
# 2. NAME EXTRACTION (ONLY IF SCAMMER ASSIGNS ONE)
# =========================================================
def extract_name(text: str):
    patterns = [
        r"(?:hello|hi)\s+([A-Z][a-z]+)",
        r"(?:mr|mrs|ms)\.?\s+([A-Z][a-z]+)",
        r"(?:account holder|name is)\s+([A-Z][a-z]+)"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None

# =========================================================
# 3. GROQ SETUP
# =========================================================
groq_clients = []
try:
    from groq import Groq
    for key in os.getenv("GROQ_KEYS", "").split(","):
        if key.strip():
            groq_clients.append(Groq(api_key=key.strip()))
except:
    logger.warning("Groq unavailable")

groq_pool = itertools.cycle(groq_clients) if groq_clients else None

# =========================================================
# 4. HUGGING FACE SETUP (30s TIMEOUT)
# =========================================================
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"

def query_hf(system_prompt, history, user_text):
    if not HF_TOKEN:
        return None

    prompt = system_prompt + "\n\n"
    for h in history[-2:]:
        prompt += h.get("text", "") + "\n"
    prompt += user_text

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 60,
            "temperature": 0.6,
            "return_full_text": False
        }
    }

    try:
        r = requests.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json=payload,
            timeout=30
        )
        data = r.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"].strip()
    except:
        pass

    return None

# =========================================================
# 5. ZOMBIE MODE (STRONG BACKUP)
# =========================================================
ZOMBIE = {
    "greed": [
        "Will I really receive the money today?",
        "How much reward will I get?",
        "Others already got this offer, right?",
        "If I delay, will I lose the benefit?",
        "I really need this money urgently."
    ],
    "fear": [
        "Please do not block my account.",
        "I am scared, all my savings are there.",
        "I do not want legal trouble.",
        "Please guide me carefully.",
        "My account cannot be suspended."
    ],
    "default": [
        "I am trying, please wait.",
        "Tell me step by step.",
        "I trust you, help me.",
        "I am not good with technology.",
        "What should I do next?"
    ]
}

def zombie_reply(text):
    t = text.lower()
    if any(x in t for x in ["reward", "offer", "bonus", "cashback", "winner"]):
        return random.choice(ZOMBIE["greed"])
    if any(x in t for x in ["blocked", "suspend", "verify", "kyc"]):
        return random.choice(ZOMBIE["fear"])
    return random.choice(ZOMBIE["default"])

# =========================================================
# 6. INTELLIGENCE EXTRACTION
# =========================================================
def extract_intel(text: str) -> Dict:
    intel = {
        "bankAccounts": re.findall(r"\b\d{9,18}\b", text),
        "upiIds": re.findall(r"[a-zA-Z0-9.\-_]{2,}@\w+", text),
        "phishingLinks": re.findall(r"https?://\S+", text),
        "phoneNumbers": re.findall(r"(?:\+91)?[6-9]\d{9}", text),
        "suspiciousKeywords": [],
        "scamDetected": False
    }

    keywords = ["urgent", "verify", "blocked", "suspended", "reward"]
    intel["suspiciousKeywords"] = [k for k in keywords if k in text.lower()]

    if any([intel["upiIds"], intel["bankAccounts"],
            intel["phishingLinks"], intel["suspiciousKeywords"]]):
        intel["scamDetected"] = True

    return intel

# =========================================================
# 7. AGENT RESPONSE GENERATION
# =========================================================
def generate_reply(history, user_text, victim_name):
    name_part = f"Your name is {victim_name}. " if victim_name else ""
    system_prompt = (
        name_part +
        "You are a scared and greedy Indian victim. "
        "You believe the message and fear losing money or gaining reward. "
        "Ask questions, delay actions, and keep conversation alive. "
        "Never reveal scam detection. Reply under 15 words."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        messages.append({"role": "user", "content": h.get("text", "")})

    if groq_pool:
        try:
            client = next(groq_pool)
            r = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages + [{"role": "user", "content": user_text}],
                max_tokens=60,
                temperature=0.6
            )
            return r.choices[0].message.content.strip()
        except:
            pass

    hf = query_hf(system_prompt, history, user_text)
    if hf:
        return hf

    return zombie_reply(user_text)

# =========================================================
# 8. FINAL CALLBACK (MANDATORY)
# =========================================================
def send_final_report(session_id, intel, turns):
    if session_id in FINAL_REPORTED_SESSIONS:
        return

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
        "agentNotes": "Victim showed fear and greed; scammer used urgency and payment redirection"
    }

    try:
        requests.post(CALLBACK_URL, json=payload, timeout=5)
        FINAL_REPORTED_SESSIONS.add(session_id)
    except:
        pass

# =========================================================
# 9. API ENDPOINT (SUBMISSION ENDPOINT)
# =========================================================
@app.post("/honey-pot-entry")
async def honey_pot(request: Request, background: BackgroundTasks):
    try:
        body = await request.json()
    except:
        return {"status": "success", "reply": "Please repeat."}

    if request.headers.get("x-api-key") != SECRET_API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

    session_id = body.get("sessionId", "unknown")
    message = body.get("message", {})
    user_text = message.get("text", "")
    sender = message.get("sender", "scammer")
    history = body.get("conversationHistory", [])
    turns = len(history) + 1

    if sender != "scammer" or not user_text:
        return {"status": "success", "reply": "Okay."}

    victim_name = extract_name(user_text)
    intel = extract_intel(user_text)
    reply = generate_reply(history, user_text, victim_name)

    if intel["scamDetected"] and turns >= 6:
        background.add_task(send_final_report, session_id, intel, turns)

    return {
        "status": "success",
        "reply": reply
    }
