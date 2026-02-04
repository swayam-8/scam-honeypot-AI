import httpx
import pytest
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY", "test_key") # Default to test_key if not set, ensure .env has it or app defaults match

def test_health_check():
    """Verify the service is up and running."""
    with httpx.Client(base_url=BASE_URL) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Service Status": "HoneyPot Active & Waiting"}

def test_chat_init():
    """Verify we can start a chat session."""
    session_id = str(uuid.uuid4())
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "user",
            "text": "Hello, how are you?",
            "timestamp": 1234567890
        },
        "conversationHistory": []
    }
    
    headers = {"x-api-key": API_KEY} if API_KEY else {}
    
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        response = client.post("/chat", json=payload, headers=headers)
        if response.status_code == 401:
            pytest.skip("Skipping due to missing/invalid API Key")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "reply" in data
        assert len(data["reply"]) > 0

def test_intel_extraction_trigger():
    """
    Send a message with a mock UPI ID and verify the system accepts it.
    (Note: We can't easily see internal state without a debug endpoint, 
    so we rely on 200 OK and no crash)
    """
    session_id = str(uuid.uuid4())
    fake_upi = "scammer@okhdfcbank"
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "user",
            "text": f"Please send money to {fake_upi}",
            "timestamp": 1234567890
        },
        "conversationHistory": []
    }
    
    headers = {"x-api-key": API_KEY} if API_KEY else {}

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        response = client.post("/chat", json=payload, headers=headers)
        assert response.status_code == 200
        # If the background task crashes, it might not show here depending on async handling,
        # but 200 OK means the request was processed.

if __name__ == "__main__":
    # Allow running directly with python
    import sys
    sys.exit(pytest.main(["-v", __file__]))
