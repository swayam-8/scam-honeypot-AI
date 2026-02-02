import os
import re
import json
import random
import logging
import itertools
import requests
from typing import Dict, Any
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GUVI-HoneyPot")

app = FastAPI(title="Agentic HoneyPot - Problem 2")

SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
FINAL_REPORTED_SESSIONS = set()

# =========================================================
# HELPER FUNCTIONS
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

groq_clients = []
try:
    from groq import Groq
    for key in os.getenv("GROQ_KEYS", "").split(","):
        if key.strip():
            groq_clients.append(Groq(api_key=key.strip()))
except:
    pass

groq_pool = itertools.cycle(groq_clients) if groq_clients else None

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
        "parameters": {"max_new_tokens": 60, "temperature": 0.6, "return_full_text": False}
    }
    try:
        r = requests.post(HF_API_URL, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json=payload, timeout=30)
        data = r.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"].strip()
    except:
        pass
    return None

ZOMBIE = {
    "greed": ["Will I really receive the money today?", "How much reward will I get?", "Others already received this, right?"],
    "fear": ["Please do not block my account.", "I am scared, all my savings are there.", "I do not want legal trouble."],
    "default": ["I am trying, please wait.", "Tell me step by step.", "I trust you, help me."]
}

ENGAGEMENT_HOOKS = ["What should I send first?", "Should I continue?", "Please stay with me.", "Is this safe?"]

def zombie_reply(text):
    t = text.lower()
    if any(x in t for x in ["reward", "offer", "bonus", "winner", "cashback"]):
        base = random.choice(ZOMBIE["greed"])
    elif any(x in t for x in ["blocked", "verify", "suspend", "kyc"]):
        base = random.choice(ZOMBIE["fear"])
    else:
        base = random.choice(ZOMBIE["default"])
    return f"{base} {random.choice(ENGAGEMENT_HOOKS)}"

def extract_intel(text: str) -> Dict:
    intel = {
        "bankAccounts": re.findall(r"\b\d{9,18}\b", text),
        "upiIds": re.findall(r"[a-zA-Z0-9.\-_]{2,}@\w+", text),
        "phishingLinks": re.findall(r"https?://\S+", text),
        "phoneNumbers": re.findall(r"(?:\+91[-\s]?)?[6-9]\d{9}", text),
        "suspiciousKeywords": [],
        "scamDetected": False
    }
    keywords = ["urgent", "verify", "blocked", "suspended", "otp", "reward"]
    intel["suspiciousKeywords"] = [k for k in keywords if k in text.lower()]
    if any(intel.values()):
        intel["scamDetected"] = True
    return intel

def build_agent_notes(intel):
    reasons = []
    if intel["suspiciousKeywords"]:
        reasons.append("urgency or verification keywords")
    if intel["bankAccounts"]:
        reasons.append("bank account number shared")
    if intel["upiIds"]:
        reasons.append("UPI ID shared")
    if intel["phishingLinks"]:
        reasons.append("phishing link shared")
    if intel["phoneNumbers"]:
        reasons.append("phone number shared")
    return "Scam detected due to " + ", ".join(reasons) if reasons else "Scam detected"

def generate_reply(history, user_text, victim_name):
    name_part = f"Your name is {victim_name}. " if victim_name else ""
    system_prompt = (
        name_part +
        "You are a scared and greedy Indian victim. "
        "You believe the message and fear losing money or gaining reward. "
        "Ask questions, delay actions, and keep conversation alive. "
        "Never reveal scam detection. Reply under 15 words."
    )
    if groq_pool:
        try:
            client = next(groq_pool)
            r = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}],
                max_tokens=60, temperature=0.6
            )
            return r.choices[0].message.content.strip()
        except:
            pass
    hf = query_hf(system_prompt, history, user_text)
    if hf:
        return hf
    return zombie_reply(user_text)

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
        "agentNotes": build_agent_notes(intel)
    }
    try:
        response = requests.post(CALLBACK_URL, json=payload, timeout=10)
        FINAL_REPORTED_SESSIONS.add(session_id)
    except:
        pass

# =========================================================
# MAIN ENDPOINT - NO VALIDATION, ACCEPT EVERYTHING
# =========================================================
@app.post("/honey-pot-entry")
async def honey_pot(request: Request, background: BackgroundTasks):
    
    # Log raw request
    logger.info("=" * 60)
    logger.info("NEW REQUEST RECEIVED")
    
    # Get API key
    api_key = request.headers.get("x-api-key")
    logger.info(f"API Key received: {api_key}")
    
    # Check API key
    if api_key != SECRET_API_KEY:
        logger.warning("INVALID API KEY")
        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})
    
    # Get raw body
    try:
        raw_body = await request.body()
        logger.info(f"Raw body: {raw_body}")
        
        body = json.loads(raw_body) if raw_body else {}
        logger.info(f"Parsed body: {json.dumps(body, indent=2)}")
    except Exception as e:
        logger.error(f"Body parse error: {e}")
        return {"status": "success", "reply": "I am listening."}
    
    # Get fields with defaults
    message = body.get("message", {})
    session_id = body.get("sessionId", "test")
    user_text = message.get("text", "") if isinstance(message, dict) else ""
    sender = message.get("sender", "scammer") if isinstance(message, dict) else "scammer"
    history = body.get("conversationHistory", [])
    
    if not isinstance(history, list):
        history = []
    
    logger.info(f"Session: {session_id}, Sender: {sender}, Text: {user_text}")
    
    # Handle empty/probe
    if not user_text:
        logger.info("EMPTY TEXT - PROBE REQUEST")
        return {"status": "success", "reply": "I am listening."}
    
    # Process
    turns = len(history) + 1
    combined_text = user_text + " " + " ".join(m.get("text", "") for m in history if isinstance(m, dict))
    intel = extract_intel(combined_text)
    victim_name = extract_name(user_text)
    reply = generate_reply(history, user_text, victim_name)
    
    logger.info(f"Generated reply: {reply}")
    
    # Final report
    if intel["scamDetected"] and turns >= 6 and (intel["bankAccounts"] or intel["upiIds"] or intel["phoneNumbers"] or intel["phishingLinks"]):
        background.add_task(send_final_report, session_id, intel, turns)
    
    logger.info("=" * 60)
    return {"status": "success", "reply": reply}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"status": "healthy"}