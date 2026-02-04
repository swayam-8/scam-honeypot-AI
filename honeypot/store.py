# In-memory session storage
sessions = {}

def get_or_create_session(session_id: str):
    """
    Get existing session or create new one.
    
    Returns session object with intelligence tracking.
    """
    if session_id not in sessions:
        sessions[session_id] = {
            "sessionId": session_id,
            "totalMessagesExchanged": 0,
            "scamDetected": True,
            "conversationHistory": [],
            "extractedIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },
            "report_sent": False
        }
    return sessions[session_id]

def add_message_to_session(session_id: str, message: dict):
    """Add message to conversation history."""
    session = sessions.get(session_id)
    if session:
        session["conversationHistory"].append(message)

def update_session(session_id: str, intelligence: dict):
    """
    Update session with extracted intelligence.
    Merges new data while avoiding duplicates.
    """
    session = get_or_create_session(session_id)
    
    for key, values in intelligence.items():
        if key in session["extractedIntelligence"]:
            current = session["extractedIntelligence"][key]
            for item in values:
                if item and item not in current:
                    current.append(item)

def should_send_report(session_id: str) -> bool:
    """
    Determine if final report should be sent.
    
    Criteria:
    - >= 5 messages exchanged OR
    - Critical intel (UPI/bank/phone) + >= 3 messages
    """
    session = sessions.get(session_id)
    if not session or session.get("report_sent"):
        return False
    
    msg_count = session["totalMessagesExchanged"]
    intel = session["extractedIntelligence"]
    
    # Enough messages
    if msg_count >= 5:
        return True
    
    # Critical data extracted
    has_critical = (
        len(intel.get("upiIds", [])) > 0 or
        len(intel.get("bankAccounts", [])) > 0 or
        len(intel.get("phoneNumbers", [])) > 0
    )
    
    if has_critical and msg_count >= 3:
        return True
    
    return False

def mark_report_sent(session_id: str):
    """Mark that report has been sent."""
    session = sessions.get(session_id)
    if session:
        session["report_sent"] = True

def get_session(session_id: str):
    """Retrieve session data."""
    return sessions.get(session_id)

def get_all_sessions():
    """Get all sessions for monitoring."""
    return sessions
