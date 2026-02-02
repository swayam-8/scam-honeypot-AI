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
# 10. API ENDPOINT
# =========================================================
@app.post("/honey-pot-entry")
async def honey_pot(request: Request, background: BackgroundTasks):
    
    # Log incoming request
    logger.info("=" * 60)
    logger.info("Received new request")
    
    # API key check FIRST
    api_key = request.headers.get("x-api-key")
    logger.info(f"API Key present: {bool(api_key)}")
    
    if not api_key or api_key != SECRET_API_KEY:
        logger.warning("Invalid or missing API key")
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid API Key"}
        )

    # Parse JSON safely
    try:
        body = await request.json()
        logger.info(f"Request body parsed successfully")
        logger.info(f"Body keys: {list(body.keys()) if isinstance(body, dict) else 'Not a dict'}")
    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON body"}
        )

    # Validate body structure
    if not isinstance(body, dict):
        logger.error("Body is not a dictionary")
        return JSONResponse(
            status_code=400,
            content={"detail": "Request body must be a JSON object"}
        )

    # Handle probe/health check requests
    if "message" not in body or "sessionId" not in body:
        logger.info("Probe request detected")
        return {
            "status": "success",
            "reply": "Endpoint reachable"
        }

    message = body.get("message")
    session_id = body.get("sessionId", "unknown")
    
    logger.info(f"Session ID: {session_id}")
    
    # Validate message structure
    if not isinstance(message, dict):
        logger.error("Message is not a dictionary")
        return {
            "status": "success",
            "reply": "Endpoint reachable"
        }

    user_text = message.get("text", "")
    sender = message.get("sender", "scammer")
    history = body.get("conversationHistory", [])
    
    # Ensure history is a list
    if not isinstance(history, list):
        history = []
    
    turns = len(history) + 1

    # Log conversation details
    logger.info(f"Sender: {sender}, Turns: {turns}, Text length: {len(user_text)}")
    logger.info(f"User text: {user_text[:100]}...")

    # If no text or wrong sender
    if sender != "scammer" or not user_text:
        logger.warning("Empty text or wrong sender")
        return {
            "status": "success",
            "reply": "Okay."
        }

    # Combine all conversation text for intelligence extraction
    combined_text = user_text + " " + " ".join(
        m.get("text", "") for m in history if isinstance(m, dict)
    )

    # Extract intelligence
    intel = extract_intel(combined_text)
    logger.info(f"Intelligence extracted:")
    logger.info(f"  - Bank Accounts: {len(intel['bankAccounts'])}")
    logger.info(f"  - UPI IDs: {len(intel['upiIds'])}")
    logger.info(f"  - Links: {len(intel['phishingLinks'])}")
    logger.info(f"  - Phone Numbers: {len(intel['phoneNumbers'])}")
    logger.info(f"  - Keywords: {intel['suspiciousKeywords']}")
    logger.info(f"  - Scam Detected: {intel['scamDetected']}")

    # Extract victim name
    victim_name = extract_name(user_text)
    if victim_name:
        logger.info(f"Victim name detected: {victim_name}")

    # Generate reply
    reply = generate_reply(history, user_text, victim_name)
    logger.info(f"Generated reply: {reply}")

    # Check if we should send final report
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
        logger.info(f"Triggering final report for session {session_id}")
        background.add_task(send_final_report, session_id, intel, turns)
    else:
        logger.info(f"Not triggering report - Scam: {intel['scamDetected']}, Turns: {turns}, Critical Intel: {bool(intel['bankAccounts'] or intel['upiIds'] or intel['phoneNumbers'] or intel['phishingLinks'])}")

    logger.info("=" * 60)
    
    return {
        "status": "success",
        "reply": reply
    }


# =========================================================
# 11. HEALTH CHECK ENDPOINT
# =========================================================
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "GUVI HoneyPot API",
        "groq_available": bool(groq_clients),
        "hf_available": bool(HF_TOKEN)
    }