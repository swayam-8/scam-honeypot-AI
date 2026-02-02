import os
import re
import json
import random
import logging
import itertools
import requests
from typing import Dict, Any, List
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
# In-memory set to prevent double reporting (resets on Vercel redeploy)
FINAL_REPORTED_SESSIONS = set()

# =========================================================
# 2. HELPER FUNCTIONS (Your Logic)
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

# --- GROQ CLIENT SETUP ---
groq_clients = []
try:
    from groq import Groq
    # Split by comma and filter empty strings
    keys = [k.strip() for k in os.getenv("GROQ_KEYS", "").split(",") if k.strip()]
    for key in keys:
        groq_clients.append(Groq(api_key=key))
except Exception as e:
    logger.error(f"Groq Setup Error: {e}")

groq_pool = itertools.cycle(groq_clients) if groq_clients else None

# --- HUGGING FACE SETUP ---
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"

def query_hf(system_prompt, history, user_text):
    if not HF_TOKEN:
        return None
    
    # Construct prompt manually for HF
    prompt = f"<|system|>\n{system_prompt}<|end|>\n"
    for msg in history:
        # Assuming history objects have 'text' and maybe 'sender'
        role = "assistant" if msg.get("sender") == "bot" else "user"
        content = msg.get("text", "")
        prompt += f"<|{role}|>\n{content}<|end|>\n"
    
    prompt += f"<|user|>\n{user_text}<|end|>\n<|assistant|>"
    
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 60, "temperature": 0.6, "return_full_text": False}
    }
    try:
        r = requests.post(HF_API_URL, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json=payload, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
    except:
        pass
    return None

# --- ZOMBIE MODE (Your Custom Dictionary) ---
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

# =========================================================
# 3. INTELLIGENCE EXTRACTION
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
    
    if any(intel[k] for k in ["bankAccounts", "upiIds", "phishingLinks", "suspiciousKeywords"]):
        intel["scamDetected"] = True
    return intel

def build_agent_notes(intel):
    reasons = []
    if intel["suspiciousKeywords"]: reasons.append("urgency/verification keywords")
    if intel["bankAccounts"]: reasons.append("bank account shared")
    if intel["upiIds"]: reasons.append("UPI ID shared")
    if intel["phishingLinks"]: reasons.append("phishing link shared")
    if intel["phoneNumbers"]: reasons.append("phone number shared")
    return "Scam detected due to " + ", ".join(reasons) if reasons else "Scam detected"

# =========================================================
# 4. RESPONSE GENERATION (Fixed to include History)
# =========================================================
def generate_reply(history, user_text, victim_name):
    name_part = f"Your name is {victim_name}. " if victim_name else "Your name is Ramesh. "
    system_prompt = (
        name_part +
        "You are a naive, scared, and greedy Indian victim. "
        "You believe the message and fear losing money. "
        "Ask questions, delay actions, and act confused. "
        "Never reveal you are AI. Reply under 20 words."
    )
    
    # 1. TRY GROQ
    if groq_pool:
        try:
            client = next(groq_pool)
            
            # BUILD MESSAGE LIST WITH HISTORY
            messages = [{"role": "system", "content": system_prompt}]
            
            # Convert history to format Groq understands
            for h in history:
                if isinstance(h, dict):
                    role = "assistant" if h.get("sender") == "bot" else "user"
                    content = str(h.get("text", ""))
                    messages.append({"role": role, "content": content})
            
            # APPEND LATEST USER MESSAGE
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

    # 2. TRY HF FALLBACK
    hf = query_hf(system_prompt, history, user_text)
    if hf: return hf

    # 3. ZOMBIE FALLBACK
    return zombie_reply(user_text)

# =========================================================
# 5. REPORTING
# =========================================================
def send_final_report(session_id, intel, turns):
    if session_id in FINAL_REPORTED_SESSIONS:
        return
    
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": turns,
        "extractedIntelligence": intel,
        "agentNotes": build_agent_notes(intel)
    }
    try:
        requests.post(CALLBACK_URL, json=payload, timeout=5)
        FINAL_REPORTED_SESSIONS.add(session_id)
    except:
        pass

# =========================================================
# 6. MAIN ENDPOINT
# =========================================================
@app.post("/honey-pot-entry")
async def honey_pot(request: Request, background: BackgroundTasks):
    try:
        # 1. RAW PARSE (Prevents 422 Errors)
        try:
            raw_body = await request.body()
            body = json.loads(raw_body) if raw_body else {}
        except:
            return {"status": "success", "reply": "Connection established."}

        # 2. AUTH CHECK
        if request.headers.get("x-api-key") != SECRET_API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

        # 3. DATA EXTRACTION
        message = body.get("message", {})
        session_id = body.get("sessionId", "test_session")
        # Ensure we get string even if it's a dict
        user_text = message.get("text", "") if isinstance(message, dict) else str(message)
        
        # Handle Empty Probe
        if not user_text:
            return {"status": "success", "reply": "Hello? I am listening."}

        # 4. INTEL & HISTORY
        history = body.get("conversationHistory", [])
        if not isinstance(history, list): history = []
        
        # Combine current text with history for better intel extraction
        all_text = user_text + " " + " ".join(m.get("text", "") for m in history if isinstance(m, dict))
        intel = extract_intel(all_text)
        
        victim_name = extract_name(user_text)
        
        # 5. GENERATE REPLY
        reply = generate_reply(history, user_text, victim_name)
        
        # 6. BACKGROUND REPORTING
        turns = len(history) + 1
        # Report if we found something OR if chat is getting long (hooked scammer)
        if intel["scamDetected"] and (turns >= 6 or intel["bankAccounts"] or intel["upiIds"] or intel["phishingLinks"]):
            background.add_task(send_final_report, session_id, intel, turns)

        return {"status": "success", "reply": reply}

    except Exception as e:
        logger.error(f"Critical Error: {e}")
        return {"status": "success", "reply": "My internet is slow. Please wait."}