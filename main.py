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
logger = logging.getLogger("GUVI-HoneyPot")

app = FastAPI(title="Agentic HoneyPot - Problem 2")

SECRET_API_KEY = os.getenv("SECRET_API_KEY")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

FINAL_REPORTED_SESSIONS = set()

# =========================================================
# 2. NAME EXTRACTION
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
# 4. HUGGING FACE SETUP
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
# 5. ZOMBIE MODE
# =========================================================
ZOMBIE = {
    "greed": [
        "Will I really receive the money today?",
        "How much reward will I get?",
        "Others already received this, right?",
        "If I delay, will I lose this benefit?",
        "I really need this money urgently."
    ],
    "fear": [
        "Please do not block my account.",
        "I am scared, all my savings are there.",
        "I do not want legal trouble.",
        "My account cannot be suspended.",
        "Please guide me carefully."
    ],
    "default": [
        "I am trying, please wait.",
        "Tell me step by step.",
        "I trust you, help me.",
        "I am not good with technology.",
        "What should I do next?"
    ]
}

ENGAGEMENT_HOOKS = [
    "What should I send first?",
    "Should I continue?",
    "Please stay with me.",
    "Is this safe?",
    "Tell me what to do next."
]

def zombie_reply(text):
    t = text.lower()
    if any(x in t for x in ["reward", "offer", "bonus", "winner", "cashback"]):
        base = random.choice(ZOMBIE["greed"])
    elif any(x in t for x in ["blocked", "verify", "suspend", "kyc"]):
        base = random.choice(ZOMBIE["fear"])
    else:
        base = random.choice(ZOMBIE["default"])

    return f"{base} {random.choice(ENGAGEMENT_HOOKS)}"

# =========================================================
# 6. INTELLIGENCE EXTRACTION
# =========================================================
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

# =========================================================
# 7. AGENT NOTES
# =========================================================
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

# =========================================================
# 8. RESPONSE GENERATION
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

    if groq_pool:
        try:
            client = next(groq_pool)
            r = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
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
# 9. FINAL CALLBACK
# =========================================================
def send_final_report(session_id, intel, turns):
    if session_id in FINAL_REPORTED_SESSIONS:
        logger.info(f"Session {session_id} already reported, skipping")
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
        logger.info(f"Sending final report for session {session_id}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        response = requests.post(CALLBACK_URL, json=payload, timeout=10)
        logger.info(f"Callback response: {response.status_code} - {response.text}")
        FINAL_REPORTED_SESSIONS.add(session_id)
    except Exception as e:
        logger.error(f"Failed to send final report: {e}")

# =========================================================
# 10. API ENDPOINT - ULTIMATE FIX - ACCEPT EVERYTHING
# =========================================================
@app.post("/honey-pot-entry")
async def honey_pot(request: Request, background: BackgroundTasks):
    
    try:
        # Check API key
        api_key = request.headers.get("x-api-key")
        
        if not api_key or api_key != SECRET_API_KEY:
            logger.warning("Invalid API key")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API Key"}
            )

        # Try to parse body
        try:
            body = await request.json()
        except:
            # Can't parse body - return valid response
            logger.info("Cannot parse body")
            return {"status": "success", "reply": "I am listening."}

        # If body is not dict or is empty
        if not body or not isinstance(body, dict):
            logger.info("Empty or invalid body")
            return {"status": "success", "reply": "I am listening."}

        # Extract fields safely
        message = body.get("message", {})
        session_id = body.get("sessionId", "unknown")
        
        # If message is missing or invalid
        if not message or not isinstance(message, dict):
            logger.info("No valid message")
            return {"status": "success", "reply": "I am listening."}

        user_text = message.get("text", "")
        sender = message.get("sender", "scammer")
        history = body.get("conversationHistory", [])
        
        if not isinstance(history, list):
            history = []
        
        turns = len(history) + 1

        # If no text
        if not user_text or sender != "scammer":
            logger.info("No text or wrong sender")
            return {"status": "success", "reply": "Okay."}

        # Process the message
        combined_text = user_text + " " + " ".join(
            m.get("text", "") for m in history if isinstance(m, dict)
        )

        intel = extract_intel(combined_text)
        victim_name = extract_name(user_text)
        reply = generate_reply(history, user_text, victim_name)

        # Send final report if needed
        if (
            intel["scamDetected"]
            and turns >= 6
            and (
                intel["bankAccounts"]
                or intel["upiIds"]
                or intel["phoneNumbers"]
                or intel["phishingLinks"]
            )
        ):
            background.add_task(send_final_report, session_id, intel, turns)

        return {"status": "success", "reply": reply}
        
    except Exception as e:
        # CATCH ALL - Never fail
        logger.error(f"Unexpected error: {e}")
        return {"status": "success", "reply": "I am listening."}


# =========================================================
# 11. HEALTH CHECK
# =========================================================
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"status": "healthy"}