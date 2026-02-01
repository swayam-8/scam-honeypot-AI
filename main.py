# import os
# import re
# import logging
# import random
# import itertools
# import requests
# from typing import List, Optional, Dict, Any

# from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
# from pydantic import BaseModel, Field
# from dotenv import load_dotenv

# # =========================================================
# # 1. CONFIGURATION
# # =========================================================
# load_dotenv()
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("HoneyPot")

# app = FastAPI(title="GUVI Top 250 - Unkillable Agent")

# # CALLBACK URL (Official Hackathon Endpoint)
# CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
# SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")

# # =========================================================
# # 2. MACHINE GUN – GROQ (PRIMARY AI)
# # =========================================================
# # Logic: Split keys by comma, strip spaces, remove quotes to prevent "400 Bad Request"
# groq_key_list = [
#     k.strip().replace('"', '').replace("'", "") 
#     for k in os.getenv("GROQ_KEYS", "").split(",") 
#     if k.strip() and "key_goes_here" not in k
# ]
# groq_clients = []

# try:
#     from groq import Groq
#     for key in groq_key_list:
#         groq_clients.append(Groq(api_key=key))
# except Exception as e:
#     logger.warning(f"Groq Setup Error: {e}")

# # Create a cycle so we rotate through keys endlessly
# groq_pool = itertools.cycle(groq_clients) if groq_clients else None

# # =========================================================
# # 3. BACKUP ARSENAL – GEMINI (SECONDARY AI)
# # =========================================================
# gemini_key_list = [
#     k.strip().replace('"', '').replace("'", "") 
#     for k in os.getenv("GEMINI_KEYS", "").split(",") 
#     if k.strip() and "key_goes_here" not in k
# ]

# try:
#     import google.generativeai as genai
# except Exception as e:
#     genai = None
#     logger.warning("Gemini SDK not available")

# # =========================================================
# # 4. MEGA ZOMBIE MODE (The "Hunter" Logic)
# # =========================================================
# ZOMBIE_RESPONSES = {
#     "upi": [
#         "I typed the UPI but it says invalid merchant.",
#         "My GPay is loading again and again.",
#         "Can you send QR instead? Typing is hard.",
#         "It shows 'Payment Failed'. What to do?",
#         "Is this UPI correct? The letters are confusing.",
#         "PhonePe closed suddenly. Sending again.",
#         "It says bank server is down.",
#         "Should I send small amount (10 rs) first?",
#         "My app needs update, wait 2 minutes."
#     ],
#     "bank": [
#         "Which bank is this exactly? SBI or HDFC?",
#         "Savings or current account? The app is asking.",
#         "IFSC code looks wrong, it is not accepting.",
#         "Manager is asking too many questions at branch.",
#         "Transfer page is not opening on my phone.",
#         "I cannot find my passbook to check details.",
#         "Account number digits are confusing. Read it to me?",
#         "Can this be done tomorrow? Bank is closed.",
#         "Net banking is locked. I am trying to reset."
#     ],
#     "link": [
#         "Link is not opening. It says '404 Error'.",
#         "Screen turned white after clicking. Is it safe?",
#         "It says site not secure. Should I proceed?",
#         "Internet is very slow here, link is loading...",
#         "Can you resend the link? I deleted it.",
#         "It redirected to a blank page.",
#         "Phone says 'Malware Detected'. What is that?",
#         "Should I open on laptop or mobile?"
#     ],
#     "otp": [
#         "OTP not received yet. Resend please.",
#         "Message came but I cannot read the code.",
#         "Signal is very weak. Wait.",
#         "Code expired I think. Send new one.",
#         "I deleted message by mistake. Sorry.",
#         "Phone restarted suddenly.",
#         "Is it a 4 digit or 6 digit code?",
#         "Wait, checking my other phone."
#     ],
#     "money": [
#         "Will I really get the money immediately?",
#         "Is there any tax charge I need to pay?",
#         "Can you deduct the fee from the prize money?",
#         "I don’t have full amount right now.",
#         "Prize amount is confirmed right?",
#         "My family is asking questions. I am scared.",
#         "This is big money for me. Please don't joke.",
#         "I trust you, please help me get it."
#     ],
#     "anger": [
#         "Please don’t shout. I am trying.",
#         "I am old, give me time.",
#         "My hands are shaking, don't be angry.",
#         "Why are you angry? I am sending the money.",
#         "Network issue here. Sorry sir.",
#         "Please talk calmly. I am confused."
#     ],
#     "default": [
#         "I am confused. Tell me again?",
#         "Please explain slowly.",
#         "One minute please, app is opening.",
#         "Network issue, message not going.",
#         "I am trying. Please wait.",
#         "Say again? I didn't understand.",
#         "Screen stuck. Restarting phone.",
#         "Battery low. Doing it fast.",
#         "Still checking. Hold on."
#     ]
# }

# def zombie_reply(text: str) -> str:
#     t = text.lower()

#     if any(x in t for x in ["idiot", "stupid", "fast", "hurry", "scam", "fake", "shut"]):
#         return random.choice(ZOMBIE_RESPONSES["anger"])
#     if any(x in t for x in ["upi", "gpay", "phonepe", "paytm", "qr"]):
#         return random.choice(ZOMBIE_RESPONSES["upi"])
#     if any(x in t for x in ["bank", "account", "ifsc", "transfer"]):
#         return random.choice(ZOMBIE_RESPONSES["bank"])
#     if any(x in t for x in ["http", "link", "click", "www", "apk"]):
#         return random.choice(ZOMBIE_RESPONSES["link"])
#     if any(x in t for x in ["otp", "code", "pin", "sms"]):
#         return random.choice(ZOMBIE_RESPONSES["otp"])
#     if any(x in t for x in ["money", "amount", "rs", "rupees", "prize", "lakh"]):
#         return random.choice(ZOMBIE_RESPONSES["money"])

#     return random.choice(ZOMBIE_RESPONSES["default"])

# # =========================================================
# # 5. DATA MODELS (Strict Compliance)
# # =========================================================
# class MessageData(BaseModel):
#     sender: str
#     text: str
#     timestamp: str

# class IncomingEvent(BaseModel):
#     sessionId: str
#     message: MessageData
#     conversationHistory: List[MessageData] = []
#     metadata: Optional[Dict[str, Any]] = None

# class AgentOutput(BaseModel):
#     status: str = "success"
#     reply: str

# class Intelligence(BaseModel):
#     bankAccounts: List[str] = Field(default_factory=list)
#     upiIds: List[str] = Field(default_factory=list)
#     phishingLinks: List[str] = Field(default_factory=list)
#     phoneNumbers: List[str] = Field(default_factory=list)  # Added for compliance
#     suspiciousKeywords: List[str] = Field(default_factory=list)
#     scamDetected: bool = False
#     callback_sent: bool = False

# session_intelligence: Dict[str, Intelligence] = {}

# # =========================================================
# # 6. INTELLIGENCE EXTRACTION (The Spy)
# # =========================================================
# def extract_intel(text: str, intel: Intelligence) -> Intelligence:
#     # 1. Capture UPI IDs
#     intel.upiIds += [u for u in re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text) if u not in intel.upiIds]

#     # 2. Capture Bank Account Numbers (9-18 digits)
#     intel.bankAccounts += [n for n in re.findall(r'\b\d{9,18}\b', text) if len(n) > 9 and n not in intel.bankAccounts]

#     # 3. Capture Phishing Links
#     intel.phishingLinks += [l for l in re.findall(r'https?://\S+', text) if l not in intel.phishingLinks]
    
#     # 4. Capture Phone Numbers (Basic regex for India +91 or 10 digits)
#     intel.phoneNumbers += [p for p in re.findall(r'(?:\+91[\-\s]?)?[6-9]\d{9}', text) if p not in intel.phoneNumbers]

#     # 5. Detect Keywords
#     keywords = ["kyc", "verify", "block", "lottery", "winner", "bank", "upi", "pay", "expired", "urgent"]
#     found = [k for k in keywords if k in text.lower()]
#     intel.suspiciousKeywords += [k for k in found if k not in intel.suspiciousKeywords]

#     # 6. Mark as Scam if ANY data found
#     if found or intel.upiIds or intel.bankAccounts or intel.phishingLinks:
#         intel.scamDetected = True

#     return intel

# # =========================================================
# # 7. PERSONA (The Victim)
# # =========================================================
# def get_persona() -> str:
#     return """
#     You are the RECEIVER of the message.
#     You are a naive, non-technical victim from India.
    
#     Rules:
#     - Never give instructions.
#     - Never explain processes.
#     - Never volunteer your name.
#     - Keep replies under 15 words.
#     - Ask only one clarity question.
#     - Sound confused and worried.
#     - Never mention scam or fraud.
#     """

# # =========================================================
# # 8. RESPONSE GENERATION (The Waterfall)
# # =========================================================
# def generate_reply(history: List[MessageData], user_text: str) -> str:
#     # Build Context
#     messages = [{"role": "system", "content": get_persona()}]
#     for m in history[-6:]:
#         messages.append({
#             "role": "user" if m.sender == "scammer" else "assistant",
#             "content": m.text
#         })
#     messages.append({"role": "user", "content": user_text})

#     # --- TIER 1: GROQ (Fastest) ---
#     if groq_pool:
#         for _ in range(3):
#             try:
#                 client = next(groq_pool)
#                 return client.chat.completions.create(
#                     model="llama3-8b-8192",
#                     messages=messages,
#                     max_tokens=50,
#                     temperature=0.3,
#                     timeout=3.0 # Strict timeout to ensure speed
#                 ).choices[0].message.content.strip()
#             except Exception:
#                 continue

#     # --- TIER 2: GEMINI (Backup) ---
#     if genai and gemini_key_list:
#         try:
#             key = random.choice(gemini_key_list)
#             genai.configure(api_key=key)
#             # User requested 2.5 explicitly
#             model = genai.GenerativeModel("gemini-2.5-flash") 
#             return model.generate_content(
#                 f"{get_persona()}\nUser: {user_text}"
#             ).text.strip()
#         except Exception:
#             pass

#     # --- TIER 3: ZOMBIE MODE (Unkillable) ---
#     return zombie_reply(user_text)

# # =========================================================
# # 9. CALLBACK REPORTER (The Compliance Engine)
# # =========================================================
# def check_and_report_intel(session_id: str, intel: Intelligence, turns: int):
#     if intel.callback_sent:
#         return

#     # Trigger Condition: Scam Detected AND (High Value Data OR Long Chat)
#     if intel.scamDetected and (intel.upiIds or intel.bankAccounts or turns > 10):
#         # PAYLOAD MUST MATCH SECTION 12 OF DOCUMENT EXACTLY
#         payload = {
#             "sessionId": session_id,
#             "scamDetected": True,
#             "totalMessagesExchanged": turns,
#             "extractedIntelligence": {
#                 "bankAccounts": intel.bankAccounts,
#                 "upiIds": intel.upiIds,
#                 "phishingLinks": intel.phishingLinks,
#                 "phoneNumbers": intel.phoneNumbers,        # COMPLIANCE FIX
#                 "suspiciousKeywords": intel.suspiciousKeywords
#             },
#             "agentNotes": "Engaged via Unkillable Agent. Payment vectors extracted." # COMPLIANCE FIX
#         }
#         try:
#             requests.post(CALLBACK_URL, json=payload, timeout=5)
#             intel.callback_sent = True
#             logger.info(f"✅ Intel Reported for {session_id}")
#         except Exception as e:
#             logger.error(f"Callback failed: {e}")

# # =========================================================
# # 10. API ENDPOINT (The Gateway)
# # =========================================================
# @app.post("/honey-pot-entry", response_model=AgentOutput)
# async def entry_point(
#     event: IncomingEvent,
#     background_tasks: BackgroundTasks,
#     request: Request
# ):
#     # 1. Auth Check
#     if request.headers.get("x-api-key") != SECRET_API_KEY:
#         raise HTTPException(status_code=401, detail="Invalid API Key")

#     sid = event.sessionId
#     if sid not in session_intelligence:
#         session_intelligence[sid] = Intelligence()

#     # 2. Extract Intel (Silent Spy)
#     intel = extract_intel(event.message.text, session_intelligence[sid])
    
#     # 3. Generate Reply (Chat)
#     reply = generate_reply(event.conversationHistory, event.message.text)

#     # 4. Report in Background (Non-blocking)
#     background_tasks.add_task(
#         check_and_report_intel,
#         sid,
#         intel,
#         len(event.conversationHistory) + 1
#     )

#     return AgentOutput(reply=reply)

import os
import re
import logging
import random
import itertools
import requests
import asyncio
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# =========================================================
# 1. CONFIGURATION
# =========================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HoneyPot")

app = FastAPI(title="GUVI Top 250 - Unkillable Agent")

# ⚠️ REPLACE WITH YOUR ACTUAL RENDER URL
MY_RENDER_URL = "https://scam-honeypot-ai-fx3c.onrender.com" 

async def keep_alive():
    """Pings the server every 14 minutes to prevent sleep mode."""
    while True:
        await asyncio.sleep(14 * 60) 
        try:
            if "onrender.com" in MY_RENDER_URL:
                requests.get(MY_RENDER_URL)
                logger.info(f"💓 Heartbeat sent to {MY_RENDER_URL}")
        except Exception:
            pass

@app.on_event("startup")
async def start_heartbeat():
    asyncio.create_task(keep_alive())

CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
SECRET_API_KEY = os.getenv("SECRET_API_KEY", "team_top_250_secret")

# =========================================================
# 2. AI CLIENTS
# =========================================================
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
    logger.warning(f"Groq Setup Error: {e}")

groq_pool = itertools.cycle(groq_clients) if groq_clients else None

gemini_key_list = [
    k.strip().replace('"', '').replace("'", "") 
    for k in os.getenv("GEMINI_KEYS", "").split(",") 
    if k.strip() and "key_goes_here" not in k
]

try:
    import google.generativeai as genai
except Exception as e:
    genai = None

# =========================================================
# 3. ZOMBIE MODE (EXPANDED ARSENAL)
# =========================================================
ZOMBIE_RESPONSES = {
    "upi": [
        "I typed the UPI but it says 'Invalid Merchant'. Check again?",
        "My GPay is loading... loading... it is stuck.",
        "Can you send a QR code? Typing the spelling is hard for me.",
        "It shows 'Payment Failed: Bank Server Down'. What now?",
        "Is this a current account or savings? App is asking.",
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
        "My manager told me not to add beneficiaries. Can we do cash?",
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
        "Can I open this on my laptop? Phone is battery low.",
        "It redirected me to Google. Where do I click?",
        "Your link looks different than the bank link."
    ],
    "otp": [
        "OTP has not arrived yet. Network is weak here.",
        "I got a code 8492... wait, that was yesterday's.",
        "I cannot read the letters without my glasses. Hold on.",
        "The message says 'Do not share this code'. Should I share?",
        "My SMS storage is full. I am deleting old messages.",
        "Phone restarted automatically. One minute.",
        "Send it to my email? SMS is not working.",
        "Did you send it? I am refreshing.",
        "Wait, my wife is calling. I have to pick up."
    ],
    "anger": [
        "Please do not shout at me. I am an old man.",
        "Why are you angry? I am trying to help you.",
        "Do not use bad language or I will hang up.",
        "I am confused, please speak slowly.",
        "My BP is high, do not stress me.",
        "If you rush me, I will make mistakes.",
        "Sorry sir, I am not good with technology.",
        "Okay, okay, I am doing it fast. Don't yell."
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
        "Who is this? I forgot your name.",
        "I think I pressed the wrong button. Going back.",
        "Wait, checking with my son."
    ]
}

def zombie_reply(text: str) -> str:
    t = text.lower()
    
    # Priority 1: Anger/Urgency Management
    if any(x in t for x in ["idiot", "stupid", "fast", "hurry", "scam", "fake", "shut up", "useless"]):
        return random.choice(ZOMBIE_RESPONSES["anger"])
    
    # Priority 2: Contextual Replies
    if any(x in t for x in ["upi", "gpay", "phonepe", "paytm", "qr", "id"]):
        return random.choice(ZOMBIE_RESPONSES["upi"])
    if any(x in t for x in ["bank", "account", "ifsc", "transfer", "neft", "rtgs"]):
        return random.choice(ZOMBIE_RESPONSES["bank"])
    if any(x in t for x in ["http", "link", "click", "www", "apk", "download", "site"]):
        return random.choice(ZOMBIE_RESPONSES["link"])
    if any(x in t for x in ["otp", "code", "pin", "sms", "message"]):
        return random.choice(ZOMBIE_RESPONSES["otp"])
        
    # Priority 3: Default Confusion
    return random.choice(ZOMBIE_RESPONSES["default"])

# =========================================================
# 4. INTELLIGENCE DATA MODEL
# =========================================================
class Intelligence(BaseModel):
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)
    scamDetected: bool = False
    callback_sent: bool = False

session_intelligence: Dict[str, Intelligence] = {}

# =========================================================
# 5. INTELLIGENCE EXTRACTION
# =========================================================
def extract_intel(text: str, intel: Intelligence) -> Intelligence:
    # Regex extraction
    intel.upiIds += [u for u in re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text) if u not in intel.upiIds]
    intel.bankAccounts += [n for n in re.findall(r'\b\d{9,18}\b', text) if len(n) > 9 and n not in intel.bankAccounts]
    intel.phishingLinks += [l for l in re.findall(r'https?://\S+', text) if l not in intel.phishingLinks]
    intel.phoneNumbers += [p for p in re.findall(r'(?:\+91[\-\s]?)?[6-9]\d{9}', text) if p not in intel.phoneNumbers]
    
    keywords = ["verify", "block", "winner", "bank", "urgent"]
    found = [k for k in keywords if k in text.lower()]
    intel.suspiciousKeywords += [k for k in found if k not in intel.suspiciousKeywords]

    if found or intel.upiIds or intel.bankAccounts or intel.phishingLinks:
        intel.scamDetected = True
    return intel

# =========================================================
# 6. RESPONSE GENERATION
# =========================================================
def generate_reply(history: List[Any], user_text: str) -> str:
    # Persona Context
    system_prompt = """You are Ramesh, a naive non-technical victim from India. 
    Act confused. Never admit you are AI. Keep replies short (under 15 words)."""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Format history safely
    for m in history[-5:]:
        try:
            role = "user" if m.get('sender') == "scammer" else "assistant"
            content = m.get('text', '')
            messages.append({"role": role, "content": content})
        except:
            pass 
    
    messages.append({"role": "user", "content": user_text})

    # 1. Try Groq
    if groq_pool:
        try:
            client = next(groq_pool)
            return client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                max_tokens=60,
                temperature=0.3
            ).choices[0].message.content.strip()
        except: pass

    # 2. Try Gemini
    if genai and gemini_key_list:
        try:
            genai.configure(api_key=random.choice(gemini_key_list))
            model = genai.GenerativeModel("gemini-1.5-flash") 
            return model.generate_content(f"{system_prompt}\nUser: {user_text}").text.strip()
        except: pass

    # 3. Zombie Mode (Now with 50+ responses)
    return zombie_reply(user_text)

# =========================================================
# 7. CALLBACK REPORTER
# =========================================================
def report_intel(sid: str, intel: Intelligence, turns: int):
    if intel.callback_sent: return
    
    if intel.scamDetected and (intel.upiIds or intel.bankAccounts or turns > 8):
        payload = {
            "sessionId": sid,
            "scamDetected": True,
            "totalMessagesExchanged": turns,
            "extractedIntelligence": {
                "bankAccounts": intel.bankAccounts,
                "upiIds": intel.upiIds,
                "phishingLinks": intel.phishingLinks,
                "phoneNumbers": intel.phoneNumbers,
                "suspiciousKeywords": intel.suspiciousKeywords
            },
            "agentNotes": "Scammer detected via Unkillable Agent."
        }
        try:
            requests.post(CALLBACK_URL, json=payload, timeout=5)
            intel.callback_sent = True
            logger.info(f"✅ Reported Intel for {sid}")
        except Exception as e:
            logger.error(f"Callback Failed: {e}")

# =========================================================
# 8. API ENDPOINT (CRASH-PROOF)
# =========================================================
@app.post("/honey-pot-entry")
async def entry_point(request: Request, background_tasks: BackgroundTasks):
    if request.headers.get("x-api-key") != SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    sid = body.get("sessionId") or body.get("session_id") or "unknown_session"
    
    msg_data = body.get("message", {})
    if isinstance(msg_data, str):
        user_text = msg_data
    else:
        user_text = msg_data.get("text", "")

    if not user_text:
        return {"status": "success", "reply": "Hello? I cannot hear you."}

    if sid not in session_intelligence:
        session_intelligence[sid] = Intelligence()
    
    intel = extract_intel(user_text, session_intelligence[sid])
    
    history = body.get("conversationHistory", [])
    if not isinstance(history, list):
        history = []
    
    reply = generate_reply(history, user_text)

    background_tasks.add_task(report_intel, sid, intel, len(history) + 1)

    return {"status": "success", "reply": reply}