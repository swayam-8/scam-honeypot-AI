# honeypot/store.py
"""
Session & Conversation Storage

Tracks:
- Individual scam sessions
- Message history for context
- Extracted intelligence
- Report sending status
"""

sessions = {}

def get_or_create_session(session_id: str):
    """
    Get or create a session for a conversation.
    
    Returns session state with intelligence tracking.
    """
    if session_id not in sessions:
        sessions[session_id] = {
            "sessionId": session_id,
            "totalMessagesExchanged": 0,
            "scamDetected": True,
            "conversationHistory": [],  # Track all messages
            "extractedIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },
            "report_sent": False,
            "report_triggered": False
        }
    return sessions[session_id]

def add_message_to_session(session_id: str, message: dict):
    """
    Add a message to the conversation history.
    """
    session = sessions.get(session_id)
    if session:
        session["conversationHistory"].append(message)

def update_session(session_id: str, new_intel: dict):
    """
    Update session with newly extracted intelligence.
    
    Merges new intelligence while avoiding duplicates.
    """
    session = sessions.get(session_id)
    if not session:
        session = get_or_create_session(session_id)
    
    # Merge intelligence without duplicates
    for key, values in new_intel.items():
        if key in session["extractedIntelligence"]:
            current_list = session["extractedIntelligence"][key]
            for item in values:
                if item and item not in current_list:
                    current_list.append(item)
    
    return session

def should_send_report(session_id: str) -> bool:
    """
    Determine if final report should be sent.
    
    Criteria:
    - At least 5 scammer messages exchanged
    - OR critical intelligence found (UPI/Bank details) + 3+ messages
    - AND not already sent
    """
    session = sessions.get(session_id)
    if not session or session.get("report_sent"):
        return False
    
    # Criteria 1: Sufficient conversation depth
    if session["totalMessagesExchanged"] >= 5:
        return True
    
    # Criteria 2: Critical intelligence extracted with reasonable engagement
    has_critical = (
        len(session["extractedIntelligence"].get("upiIds", [])) > 0 or
        len(session["extractedIntelligence"].get("bankAccounts", [])) > 0 or
        len(session["extractedIntelligence"].get("phoneNumbers", [])) > 0
    )
    
    if has_critical and session["totalMessagesExchanged"] >= 3:
        return True
    
    return False

def mark_report_sent(session_id: str):
    """
    Mark that final report has been sent for this session.
    """
    session = sessions.get(session_id)
    if session:
        session["report_sent"] = True

def get_session(session_id: str):
    """
    Retrieve session data (for debugging/monitoring).
    """
    return sessions.get(session_id)

def get_all_sessions():
    """
    Get all sessions (for monitoring/analytics).
    """
    return sessions