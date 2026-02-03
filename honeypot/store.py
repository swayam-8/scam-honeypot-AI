# honeypot/store.py

sessions = {}

def get_or_create_session(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = {
            "totalMessagesExchanged": 0,
            "scamDetected": True, 
            "extractedIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },
            "report_sent": False  # <--- NEW FLAG
        }
    return sessions[session_id]

def update_session(session_id: str, new_intel: dict):
    session = sessions[session_id]
    session["totalMessagesExchanged"] += 1

    for key, values in new_intel.items():
        if key in session["extractedIntelligence"]:
            current_list = session["extractedIntelligence"][key]
            for item in values:
                if item not in current_list:
                    current_list.append(item)
    
    return session