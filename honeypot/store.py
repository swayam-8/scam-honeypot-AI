# In-memory database
# Structure: { "session_id": { "count": 0, "intel": {...}, "scam_detected": False } }
sessions = {}

def get_or_create_session(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = {
            "totalMessagesExchanged": 0,
            "scamDetected": True, # Assume true if we are engaging
            "extractedIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },
            "agentNotes": "Monitoring conversation..."
        }
    return sessions[session_id]

def update_session(session_id: str, new_intel: dict):
    session = sessions[session_id]
    
    # Increment message count (User + Agent = 2 messages per turn usually, 
    # but let's count 1 for the incoming user message)
    session["totalMessagesExchanged"] += 1

    # Merge new intelligence into existing lists (avoid duplicates)
    for key, values in new_intel.items():
        if key in session["extractedIntelligence"]:
            current_list = session["extractedIntelligence"][key]
            # Add only unique new items
            for item in values:
                if item not in current_list:
                    current_list.append(item)
    
    return session