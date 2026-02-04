import os
import re
import requests
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

def scam_intent_detected(text):
    scam_keywords = [
        "verify", "account blocked", "urgent", "suspend", "UPI", "bank account", "phishing", "payment", "OTP", "link"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in scam_keywords)

def extract_intelligence(messages):
    bank_accounts = []
    upi_ids = []
    phishing_links = []
    phone_numbers = []
    suspicious_keywords = []

    upi_pattern = r"\b\w+@\w+\b"
    bank_pattern = r"\b\d{4}-\d{4}-\d{4}\b"
    link_pattern = r"http[s]?://[^\s]+"
    phone_pattern = r"\+?\d{10,13}"
    keywords = ["urgent", "verify now", "account blocked", "OTP", "payment", "suspend"]

    for msg in messages:
        text = msg.get("text", "")
        bank_accounts += re.findall(bank_pattern, text)
        upi_ids += re.findall(upi_pattern, text)
        phishing_links += re.findall(link_pattern, text)
        phone_numbers += re.findall(phone_pattern, text)
        for kw in keywords:
            if kw in text.lower():
                suspicious_keywords.append(kw)
    return {
        "bankAccounts": list(set(bank_accounts)),
        "upiIds": list(set(upi_ids)),
        "phishingLinks": list(set(phishing_links)),
        "phoneNumbers": list(set(phone_numbers)),
        "suspiciousKeywords": list(set(suspicious_keywords))
    }

def agent_reply(message, history):
    if "account" in message.lower():
        return "Why is my account being suspended?"
    elif "upi" in message.lower():
        return "Can you explain why you need my UPI ID?"
    elif "verify" in message.lower():
        return "How do I verify my account?"
    else:
        return "Can you provide more details?"

def send_final_result(session_id, scam_detected, total_messages, intelligence, agent_notes):
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": agent_notes
    }
    try:
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=5
        )
        print("Final result sent:", response.status_code)
    except Exception as e:
        print("Error sending final result:", e)

@app.head("/")
async def head_root(request: Request):
    return Response(status_code=200)

@app.head("/honeypot")
async def head_honeypot(request: Request):
    return Response(status_code=200)

@app.post("/honeypot")
async def honeypot_endpoint(
    request: Request,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        data = await request.json()
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid JSON"})

    session_id = data.get("sessionId")
    message = data.get("message", {})
    conversation_history = data.get("conversationHistory", [])
    metadata = data.get("metadata", {})

    all_messages = conversation_history + [message]
    scam_detected = scam_intent_detected(message.get("text", ""))
    reply = agent_reply(message.get("text", ""), conversation_history)
    intelligence = extract_intelligence(all_messages)

    agent_notes = "Scammer used urgency tactics and payment redirection" if scam_detected else "No scam detected"

    response_json = {
        "status": "success",
        "reply": reply
    }

    if scam_detected and len(all_messages) >= 3:
        send_final_result(
            session_id=session_id,
            scam_detected=True,
            total_messages=len(all_messages),
            intelligence=intelligence,
            agent_notes=agent_notes
        )

    return JSONResponse(content=response_json)
