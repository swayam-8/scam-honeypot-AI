"""
Test script for the Scam HoneyPot API

Tests the /chat endpoint with various scam scenarios
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000/chat"
API_KEY = "test-api-key"

def test_ping():
    """Test with empty payload (ping)"""
    print("\n" + "="*60)
    print("TEST 1: Ping Request (Empty/Null Payload)")
    print("="*60)
    
    payload = {
        "sessionId": "ping-test",
        "message": None,
        "conversationHistory": [],
        "metadata": None
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_first_scam_message():
    """Test first scam message (no history)"""
    print("\n" + "="*60)
    print("TEST 2: First Scam Message")
    print("="*60)
    
    payload = {
        "sessionId": "scam-session-001",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately by clicking this link: http://malicious-bank.com/verify",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_follow_up_message():
    """Test follow-up message with history"""
    print("\n" + "="*60)
    print("TEST 3: Follow-up Message with Conversation History")
    print("="*60)
    
    payload = {
        "sessionId": "scam-session-001",
        "message": {
            "sender": "scammer",
            "text": "Share your UPI ID to avoid account suspension. My UPI: scammer@okhdfcbank",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately.",
                "timestamp": int(time.time() * 1000) - 5000
            },
            {
                "sender": "user",
                "text": "Why will my account be blocked? What should I do?",
                "timestamp": int(time.time() * 1000) - 3000
            }
        ],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_phishing_message():
    """Test phishing/UPI scam"""
    print("\n" + "="*60)
    print("TEST 4: Phishing Message with UPI Request")
    print("="*60)
    
    payload = {
        "sessionId": "phishing-session-002",
        "message": {
            "sender": "scammer",
            "text": "Urgent! Your PAN and Aadhar need verification. Call +919876543210 now or verify at http://bank-verify.com/kyc",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_multi_turn_conversation():
    """Test a multi-turn conversation to trigger report"""
    print("\n" + "="*60)
    print("TEST 5: Multi-Turn Conversation (4+ messages)")
    print("="*60)
    
    session_id = "multi-turn-session-003"
    
    messages = [
        "Your account is suspended due to suspicious activity. Verify now.",
        "I received your message. What should I do? My account number is 1234567890",
        "Send your UPI ID to reactivate. Use: scammer@okhdfcbank",
        "I'm scared. My UPI is victim@icici. Please help!",
        "Good. Now send Rs. 500 to verify. After that your account will be active."
    ]
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    for i, msg in enumerate(messages):
        history = []
        if i > 0:
            # Build history from previous messages
            for j in range(i):
                if j % 2 == 0:
                    history.append({
                        "sender": "scammer",
                        "text": messages[j],
                        "timestamp": int(time.time() * 1000) - (i - j) * 5000
                    })
                else:
                    history.append({
                        "sender": "user",
                        "text": f"Response to message {j}",
                        "timestamp": int(time.time() * 1000) - (i - j - 1) * 5000
                    })
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer" if i % 2 == 0 else "user",
                "text": msg,
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": history,
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        try:
            print(f"\nMessage {i+1}: {msg[:50]}...")
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Reply: {response.json().get('reply', 'N/A')}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("\n🚀 SCAM HONEYPOT API TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Ping Test", test_ping()))
    time.sleep(1)
    
    results.append(("First Scam Message", test_first_scam_message()))
    time.sleep(1)
    
    results.append(("Follow-up Message", test_follow_up_message()))
    time.sleep(1)
    
    results.append(("Phishing Message", test_phishing_message()))
    time.sleep(1)
    
    test_multi_turn_conversation()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
