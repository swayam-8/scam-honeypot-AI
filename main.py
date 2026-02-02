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
# 1. SETUP & CONFIGURATION
# =========================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GUVI-HoneyPot")

app = FastAPI(title="Agentic HoneyPot - Problem 2")

SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# In-memory deduplication (OK for hackathon)
FINAL_REPORTED_SESSIONS = set()

# =========================================================
# 2. HELPER FUNCTIONS
# =========================================================
def extract_name(text: str):
    patterns = [
        r"(?:hello|hi)\s+([A-Za-z]{3,})",
        r"(?:mr|mrs|ms)\.?\s+([A-Za-z]{3,})",
        r"(?:account holder|name is)\s+([A-Za-z]{3,})"
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
    keys = [k.strip() for k in os.getenv("GROQ_KEYS", "").split(",") if k.strip()]
    for key in keys:
        groq_clients.append(Groq(api_key=key))
except Exception as e:
    logger.error(f"Groq setup error: {e}")

groq_pool = itertools.cycle(groq_clients) if groq_clients else None

# =========================================================
# 4. HUGGINGFACE FALLBACK
# =========================================================
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"

def query_hf(system_prompt, history, user_text):
    if not HF_TOKEN:
        return None

    prompt = f"<|system|>\n{system_prompt}<|end|>\n"
    for msg in history[-4:]:
        role = "assistant" if msg.get("sender") == "bot" else "user"
        prompt += f"<|{role}|>\n{msg.get('text','')}<|end|>\n"

    prompt += f"<|user|>\n{user_text}<|end|>\n<|assistant|>"

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
            timeout=5
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
    except Exception as e:
        logger.warning(f"HF fallback failed: {e}")

    return None

# =========================================================
# 5. ZOMBIE MODE
# =========================================================
ZOMBIE = {
    "greed": [
        "Will I really get the money today?",
        "How much reward will I receive?",
        "Others already got this, right?"
    ],
    "fear": [
        "Please don't block my account.",
        "I am scared, all savings are there.",
        "I don't want legal problems."
    ],
    "default": [
        "I am trying, please wait.",
        "Tell me step by step.",
        "I trust you, please help."
    ]
}

ENGAGEMENT_HOOKS = [
    "What should I do now?",
    "Is this safe?",
    "Please stay with me.",
    "What should I send first?"
]

def zombie_reply(text: str):
    t = text.lower()
    if any(x in t for x in ["reward", "offer", "bonus", "winner", "cashback"]):
        base = random.choice(ZOMBIE["greed"])
    elif any(x in t for x in ["blocked", "verify", "suspend", "kyc", "otp"]):
        base = random.choice(ZOMBIE["fear"])
    else:
        base = random.choice(ZOMBIE["default"])
    return f"{base} {random.choice(ENGAGEMENT_HOOKS)}"

# =========================================================
# 6. INTELLIGENCE EXTRACTION
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

    if (
        intel["bankAccounts"]
        or intel["upiIds"]
        or intel["phishingLinks"]
        or intel["phoneNumbers"]
        or intel["suspiciousKeywords"]
    ):
        intel["scamDetected"] = True

    return intel

def build_agent_notes(intel):
    reasons = []
    if intel["suspiciousKeywords"]: reasons.append("urgency or verification keywords")
    if intel["bankAccounts"]: reasons.append("bank account shared")
    if intel["upiIds"]: reasons.append("UPI ID shared")
    if intel["phishingLinks"]: reasons.append("phishing link shared")
    if intel["phoneNumbers"]: reasons.append("phone number shared")
    return "Scam detected due to " + ", ".join(reasons) if reasons else "Scam detected"

# =========================================================
# 7. RESPONSE GENERATION
# =========================================================
def generate_reply(history, user_text, victim_name):
    name_part = f"Your name is {victim_name}. " if victim_name else "Your name is Ramesh. "

    system_prompt = (
        name_part +
        "You are a naive, scared and greedy Indian victim. "
        "You believe the message and fear losing money. "
        "Ask questions, delay actions, act confused. "
        "Never reveal you are AI. Reply under 20 words."
    )

    # GROQ
    if groq_pool is not None:
        try:
            client = next(groq_pool)
            messages = [{"role": "system", "content": system_prompt}]

            for h in history[-4:]:
                role = "assistant" if h.get("sender") == "bot" else "user"
                messages.append({"role": role, "content": str(h.get("text", ""))})

            messages.append({"role": "user", "content": user_text})

            r = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                max_tokens=60,
                temperature=0.6
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Groq failed: {e}")

    # HF fallback
    hf = query_hf(system_prompt, history, user_text)
    if hf:
        return hf

    # Zombie fallback
    return zombie_reply(user_text)

# =========================================================
# 8. REPORTING
# =========================================================
def send_final_report(session_id, intel, turns):
    if session_id in FINAL_REPORTED_SESSIONS:
        return

    FINAL_REPORTED_SESSIONS.add(session_id)

    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": turns,
        "extractedIntelligence": intel,
        "agentNotes": build_agent_notes(intel)
    }

    try:
        requests.post(CALLBACK_URL, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Callback failed: {e}")

# =========================================================
# 9. MAIN ENDPOINT (GUVI SAFE)
# =========================================================
@app.post("/honey-pot-entry")
async def honey_pot(request: Request, background: BackgroundTasks):

    # 🔥 GUVI TESTER SENDS EMPTY BODY — HANDLE FIRST
    raw_body = await request.body()
    if not raw_body:
        return {
            "status": "success",
            "reply": "Hello, I am listening."
        }

    # SAFE JSON PARSE
    try:
        body = json.loads(raw_body)
        if not isinstance(body, dict):
            body = {}
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Invalid JSON in request body: {e}")
        body = {}

    # AUTH
    if request.headers.get("x-api-key") != SECRET_API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

    message = body.get("message", {})
    session_id = body.get("sessionId", "test_session")

    user_text = ""
    if isinstance(message, dict):
        user_text = str(message.get("text", ""))
    elif isinstance(message, str):
        user_text = message

    if not user_text:
        return {"status": "success", "reply": "Hello? I am listening."}

    history = body.get("conversationHistory", [])
    if not isinstance(history, list):
        history = []

    combined_text = user_text + " " + " ".join(
        str(h.get("text", "")) for h in history if isinstance(h, dict) and h.get("text")
    )

    intel = extract_intel(combined_text)
    victim_name = extract_name(user_text)

    reply = generate_reply(history, user_text, victim_name)

    turns = len(history) + 1
    if intel["scamDetected"] and (
        turns >= 6 or intel["bankAccounts"] or intel["upiIds"] or intel["phishingLinks"]
    ):
        background.add_task(send_final_report, session_id, intel, turns)

    return {"status": "success", "reply": reply}

# =========================================================
# 10. HEALTH
# =========================================================
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"status": "healthy"}
