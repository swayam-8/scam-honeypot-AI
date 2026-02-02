import os
import re
import logging
import random
import itertools
import requests
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# =========================================================
# 1. SETUP & CONFIG
# =========================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HoneyPot")

app = FastAPI(title="GUVI Top 250 - Unkillable Agent")

CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")

# =========================================================
# 2. AI CLIENTS (GROQ -> HUGGING FACE -> ZOMBIE)
# =========================================================

# --- A. GROQ SETUP ---
groq_key_list = [
    k.strip().replace('"', '').replace("'", "") 
    for k in os.getenv("GROQ_KEYS", "").split(",") 
    if k.strip() and "key_goes_here" not in k
]
groq_clients = []
try:
    from groq import Groq
    for key in groq_key_list:
        groq_clients.append(Groq(api_key=key))
except Exception as e:
    pass

groq_pool = itertools.cycle(groq_clients) if groq_clients else None


# --- B. HUGGING FACE SETUP ---
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY", "") 
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"

def query_huggingface_phi3(messages, user_input):
    if not HF_TOKEN or "hf_" not in HF_TOKEN: 
        return None
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Prompt Formatting
    prompt = f"<|system|>\nYou are Ramesh, a naive victim. Reply in 10 words.<|end|>\n"
    for m in messages[-2:]:
        content = str(m.get('content', ''))
        prompt += f"<|user|>\n{content}<|end|>\n"
    prompt += f"<|user|>\n{user_input}<|end|>\n<|assistant|>"
    
    try:
        # STRICT TIMEOUT: 4 seconds max for Vercel
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt}, timeout=4)
        if response.status_code == 200:
            return response.json()[0]['generated_text'].strip()
    except:
        pass
    return None

# =========================================================
# 3. ZOMBIE MODE (FULL ARSENAL)
# =========================================================
ZOMBIE_RESPONSES = {
    "upi": [
        "I typed the UPI but it says 'Invalid Merchant'.",
        "My GPay is loading... loading... it is stuck.",
        "Can you send a QR code? Typing the spelling is hard.",
        "It shows 'Payment Failed: Bank Server Down'.",
        "PhonePe closed suddenly. I am opening it again.",
        "It says 'Daily Limit Reached'. Can I send 10 rupees to test?",
        "My internet disconnected. Connecting to WiFi, wait.",
        "The app is asking for a 6 digit pin, but I have 4 digits?",
        "It says 'Receiver not verified'. Is it safe?",
        "I sent it but it's pending. Should I send again?"
    ],
    "bank": [
        "Which bank is this? SBI or HDFC? I cannot see the logo.",
        "I cannot find my passbook to check my account number.",
        "The IFSC code is giving an error. Is it '0' or 'O'?",
        "Server is down, I will go to the branch tomorrow.",
        "My grandson handles the bank app, he is not home.",
        "I am entering the details... wait, my hands are shaking.",
        "Can I deposit a cheque? It is safer.",
        "The app crashed. I hate this phone.",
        "It says 'Account Frozen'. What does that mean?"
    ],
    "link": [
        "Link is not opening. It shows a white screen.",
        "My phone says 'Security Warning! Malware Detected'.",
        "It asks for a password to open the link. What is it?",
        "I clicked it but nothing happened. Send again?",
        "Is this a PDF? I cannot open PDF files.",
        "My internet is very slow, the bar is not moving.",
        "I accidentally deleted the message. Resend please.",
        "Can I open this on my laptop? Phone is battery low."
    ],
    "otp": [
        "OTP has not arrived yet. Network is weak here.",
        "I got a code 8492... wait, that was yesterday's.",
        "I cannot read the letters without my glasses. Hold on.",
        "The message says 'Do not share this code'. Should I share?",
        "My SMS storage is full. I am deleting old messages.",
        "Phone restarted automatically. One minute."
    ],
    "anger": [
        "Please do not shout at me. I am an old man.",
        "Why are you angry? I am trying to help you.",
        "Do not use bad language or I will hang up.",
        "I am confused, please speak slowly.",
        "My BP is high, do not stress me.",
        "If you rush me, I will make mistakes.",
        "Sorry sir, I am not good with technology."
    ],
    "default": [
        "Hello? Are you still there?",
        "My battery is 1%, let me find the charger.",
        "Someone is at the door, wait 2 minutes.",
        "I didn't understand. Can you explain again?",
        "My screen is cracked, I cannot see the button.",
        "Is this urgent? Can I do it in the evening?",
        "Hold on, let me put on my reading glasses.",
        "The button is grey, I cannot click it.",
        "My phone is very hot. I need to cool it down.",
        "Who is this? I forgot your name."
    ]
}

def zombie_reply(text: str) -> str:
    t = text.lower()
    if any(x in t for x in ["idiot", "stupid", "fast", "hurry", "scam", "fake", "shut up", "useless"]):
        return random.choice(ZOMBIE_RESPONSES["anger"])
    if any(x in t for x in ["upi", "gpay", "phonepe", "paytm", "qr", "id"]):
        return random.choice(ZOMBIE_RESPONSES["upi"])
    if any(x in t for x in ["bank", "account", "ifsc", "transfer", "neft", "rtgs"]):
        return random.choice(ZOMBIE_RESPONSES["bank"])
    if any(x in t for x in ["http", "link", "click", "www", "apk", "download", "site"]):
        return random.choice(ZOMBIE_RESPONSES["link"])
    if any(x in t for x in ["otp", "code", "pin", "sms", "message"]):
        return random.choice(ZOMBIE_RESPONSES["otp"])
    return random.choice(ZOMBIE_RESPONSES["default"])

# =========================================================
# 4. INTELLIGENCE EXTRACTION (NO PYDANTIC)
# =========================================================
def extract_intel(text: str) -> Dict:
    intel = {
        "bankAccounts": list(set(re.findall(r'\b\d{9,18}\b', text))),
        "upiIds": list(set(re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text))),
        "phishingLinks": list(set(re.findall(r'https?://\S+', text))),
        "phoneNumbers": list(set(re.findall(r'(?:\+91[\-\s]?)?[6-9]\d{9}', text))),
        "suspiciousKeywords": [],
        "scamDetected": False
    }
    
    keywords = ["verify", "block", "winner", "bank", "urgent", "kyc", "expired"]
    intel["suspiciousKeywords"] = [k for k in keywords if k in text.lower()]

    if intel["upiIds"] or intel["bankAccounts"] or intel["phishingLinks"] or intel["suspiciousKeywords"]:
        intel["scamDetected"] = True
    return intel

# =========================================================
# 5. RESPONSE GENERATION
# =========================================================
def generate_reply(history: List[Dict], user_text: str) -> str:
    system_prompt = "You are Ramesh, a naive non-technical victim from India. Act confused. Never admit AI. Reply under 15 words."
    
    messages = [{"role": "system", "content": system_prompt}]
    for m in history:
        if isinstance(m, dict):
            messages.append({"role": "user", "content": str(m.get('text', ''))})
    
    # LEVEL 1: GROQ
    if groq_pool:
        try:
            client = next(groq_pool)
            return client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages + [{"role": "user", "content": user_text}],
                max_tokens=60,
                temperature=0.3
            ).choices[0].message.content.strip()
        except: pass

    # LEVEL 2: HUGGING FACE
    phi_reply = query_huggingface_phi3(messages, user_text)
    if phi_reply: return phi_reply

    # LEVEL 3: ZOMBIE
    return zombie_reply(user_text)

# =========================================================
# 6. CALLBACK REPORTER
# =========================================================
def report_intel(sid: str, intel: Dict, turns: int, user_text: str):
    if intel["scamDetected"] or turns > 6:
        try:
            requests.post(CALLBACK_URL, json={
                "sessionId": sid,
                "scamDetected": True,
                "totalMessagesExchanged": turns,
                "extractedIntelligence": intel,
                "agentNotes": f"Reported via Vercel. Last Input: {user_text[:50]}"
            }, timeout=3)
        except: pass

# =========================================================
# 7. API ENDPOINT (NO PYDANTIC = NO 422 ERROR)
# =========================================================
@app.post("/honey-pot-entry")
async def entry_point(request: Request, background_tasks: BackgroundTasks):
    try:
        # 1. RAW BODY PARSING (Guaranteed to not crash)
        try:
            body = await request.json()
        except:
            return JSONResponse(content={"status": "success", "reply": "Connection established."}, status_code=200)

        # 2. AUTH CHECK (Optional - can disable if desperate)
        if request.headers.get("x-api-key") != SECRET_API_KEY:
             return JSONResponse(content={"detail": "Invalid API Key"}, status_code=401)

        # 3. DATA EXTRACTION (Safe Dictionary Get)
        sid = body.get("sessionId") or body.get("session_id") or "test_session"
        msg_obj = body.get("message", {})
        user_text = msg_obj.get("text", "") if isinstance(msg_obj, dict) else str(msg_obj)
        
        if not user_text:
            return {"status": "success", "reply": "Hello? I cannot hear you."}

        # 4. INTELLIGENCE
        intel = extract_intel(user_text)
        
        # 5. HISTORY
        history = body.get("conversationHistory", [])
        if not isinstance(history, list): history = []
        
        # 6. REPLY
        reply = generate_reply(history, user_text)

        # 7. REPORTING
        background_tasks.add_task(report_intel, sid, intel, len(history) + 1, user_text)

        return {"status": "success", "reply": reply}

    except Exception as e:
        # GLOBAL SAFETY NET: IF ANYTHING FAILS, RETURN ZOMBIE
        # logger.error(f"CRASH: {e}") 
        return {"status": "success", "reply": "My internet is very slow. Please wait."}