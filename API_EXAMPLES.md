# API Request & Response Examples

This file contains real-world examples of how the Agentic Honey-Pot API works.

## Scenario 1: Simple UPI Fraud Detection (First Message)

### Request
```json
{
  "sessionId": "session-upi-001",
  "message": {
    "sender": "scammer",
    "text": "Your UPI payment failed. Verify your account immediately at http://verify-upi.com/kyc",
    "timestamp": 1707000000000
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response
```json
{
  "status": "success",
  "reply": "I'm confused... What payment? I don't remember any failed transaction. What should I do?"
}
```

### Intelligence Extracted
```json
{
  "bankAccounts": [],
  "upiIds": [],
  "phishingLinks": ["http://verify-upi.com/kyc"],
  "phoneNumbers": [],
  "suspiciousKeywords": ["verify", "account", "failed"]
}
```

---

## Scenario 2: Bank Account Fraud (Multi-turn Engagement)

### Turn 1 - Initial Scam Message

**Request:**
```json
{
  "sessionId": "session-bank-002",
  "message": {
    "sender": "scammer",
    "text": "Your bank account is suspended due to suspicious activity. Verify your details immediately.",
    "timestamp": 1707000000000
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "WhatsApp",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Oh no! What? My account is suspended? Why? I didn't do anything wrong. What should I do?"
}
```

---

### Turn 2 - Requesting Account Details

**Request:**
```json
{
  "sessionId": "session-bank-002",
  "message": {
    "sender": "scammer",
    "text": "Provide your account number and bank name to verify. Also share your UPI ID.",
    "timestamp": 1707000005000
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account is suspended due to suspicious activity. Verify your details immediately.",
      "timestamp": 1707000000000
    },
    {
      "sender": "user",
      "text": "Oh no! What? My account is suspended? Why? I didn't do anything wrong. What should I do?",
      "timestamp": 1707000002000
    }
  ],
  "metadata": {
    "channel": "WhatsApp",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "I'm scared... Is this really from the bank? My account number is 987654321012. I have ICICI. My UPI is victim123@icici. Please help me!"
}
```

### Intelligence Extracted at Turn 2
```json
{
  "bankAccounts": ["987654321012"],
  "upiIds": ["victim123@icici"],
  "phishingLinks": [],
  "phoneNumbers": [],
  "suspiciousKeywords": ["suspended", "suspicious", "activity", "verify"]
}
```

---

### Turn 3 - Payment Request

**Request:**
```json
{
  "sessionId": "session-bank-002",
  "message": {
    "sender": "scammer",
    "text": "Send ₹500 to this UPI to reactivate: scammer@okhdfcbank. Your account will be active in 5 minutes.",
    "timestamp": 1707000010000
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account is suspended due to suspicious activity. Verify your details immediately.",
      "timestamp": 1707000000000
    },
    {
      "sender": "user",
      "text": "Oh no! What? My account is suspended? Why? I didn't do anything wrong. What should I do?",
      "timestamp": 1707000002000
    },
    {
      "sender": "scammer",
      "text": "Provide your account number and bank name to verify. Also share your UPI ID.",
      "timestamp": 1707000005000
    },
    {
      "sender": "user",
      "text": "I'm scared... Is this really from the bank? My account number is 987654321012. I have ICICI. My UPI is victim123@icici. Please help me!",
      "timestamp": 1707000007000
    }
  ],
  "metadata": {
    "channel": "WhatsApp",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "I'm very worried! Will it really take only 5 minutes? Do I need to send from my ICICI app? I have very limited balance... can I send less?"
}
```

### Intelligence Extracted at Turn 3
```json
{
  "bankAccounts": ["987654321012"],
  "upiIds": ["scammer@okhdfcbank", "victim123@icici"],
  "phishingLinks": [],
  "phoneNumbers": [],
  "suspiciousKeywords": ["suspended", "suspicious", "activity", "verify", "account", "reactivate"]
}
```

---

### Turn 4 - Persistence

**Request:**
```json
{
  "sessionId": "session-bank-002",
  "message": {
    "sender": "scammer",
    "text": "Send Rs 500 now! Don't worry about balance. Use your debit card if needed. My number is +919876543210 if you need help.",
    "timestamp": 1707000015000
  },
  "conversationHistory": [
    // ... [4 previous messages combined for context] ...
  ],
  "metadata": {
    "channel": "WhatsApp",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Ok ok... I'm doing it now. My hands are shaking. Is your number the one to call if there's any problem?"
}
```

### Intelligence Extracted at Turn 4
```json
{
  "bankAccounts": ["987654321012"],
  "upiIds": ["scammer@okhdfcbank", "victim123@icici"],
  "phishingLinks": [],
  "phoneNumbers": ["+919876543210"],
  "suspiciousKeywords": ["suspended", "suspicious", "activity", "verify", "account", "reactivate", "debit card", "urgent"]
}
```

**At this point (4 messages exchanged), the system triggers the final report:**

```json
{
  "sessionId": "session-bank-002",
  "scamDetected": true,
  "totalMessagesExchanged": 4,
  "extractedIntelligence": {
    "bankAccounts": ["987654321012"],
    "upiIds": ["scammer@okhdfcbank", "victim123@icici"],
    "phishingLinks": [],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["suspended", "suspicious", "activity", "verify", "account", "reactivate", "debit card", "urgent"]
  },
  "agentNotes": "Scammer used urgency and authority tactics on WhatsApp. Requested bank account number, UPI ID, and payment. Provided contact phone number +919876543210. Classic account suspension scam pattern."
}
```

---

## Scenario 3: Phishing Link Attack

### Request
```json
{
  "sessionId": "session-phishing-003",
  "message": {
    "sender": "scammer",
    "text": "URGENT: Your PAN card has expired. Update it now: http://pan-update-verify.com/aadhar-kyc. Call +91 98765 43210 for assistance.",
    "timestamp": 1707000000000
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "Email",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response
```json
{
  "status": "success",
  "reply": "My PAN expired? But I updated it last year! Is this a scam? Should I really click that link? I'm not sure..."
}
```

### Intelligence Extracted
```json
{
  "bankAccounts": [],
  "upiIds": [],
  "phishingLinks": ["http://pan-update-verify.com/aadhar-kyc"],
  "phoneNumbers": ["+919876543210"],
  "suspiciousKeywords": ["urgent", "pan", "expired", "update", "aadhar", "kyc", "verify"]
}
```

---

## Scenario 4: Complex Multi-Channel Attack

### Request (WhatsApp with Links & UPI)
```json
{
  "sessionId": "session-complex-004",
  "message": {
    "sender": "scammer",
    "text": "Congrats! You won ₹10 lakhs! Verify your identity at www.lottery-claim.in. Send your bank a/c: XXXXXXXXXX, UPI: lucky@okhdfcbank, and contact number +91 98765 43210.",
    "timestamp": 1707000000000
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "WhatsApp",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response
```json
{
  "status": "success",
  "reply": "Wait, really?? I won a lottery? I never even participated... Is this real? Are you sure?"
}
```

### Intelligence Extracted
```json
{
  "bankAccounts": ["XXXXXXXXXX"],
  "upiIds": ["lucky@okhdfcbank"],
  "phishingLinks": ["www.lottery-claim.in"],
  "phoneNumbers": ["+919876543210"],
  "suspiciousKeywords": ["congrats", "won", "verify", "identity", "lottery", "claim"]
}
```

---

## Error Scenarios

### Missing Message Text (Ping/Connection Check)

**Request:**
```json
{
  "sessionId": "ping-001",
  "message": null,
  "conversationHistory": [],
  "metadata": null
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Connection Successful. HoneyPot is active."
}
```

---

### Invalid API Key

**Request (with wrong API key):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: wrong-key" \
  -d '{"sessionId": "sess-001", "message": {"text": "test"}}'
```

**Response:**
```json
{
  "detail": "Unauthorized"
}
```

HTTP Status: **401**

---

## Final Report Callback Format

**Sent to:** `POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult`

**Payload:**
```json
{
  "sessionId": "session-bank-002",
  "scamDetected": true,
  "totalMessagesExchanged": 4,
  "extractedIntelligence": {
    "bankAccounts": ["987654321012"],
    "upiIds": ["scammer@okhdfcbank", "victim123@icici"],
    "phishingLinks": [],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["suspended", "suspicious", "verify", "account", "urgent", "debit card"]
  },
  "agentNotes": "Scammer impersonated bank on WhatsApp. Used urgency tactics and social engineering. Extracted bank account, UPI, and phone number. Classic account suspension fraud pattern."
}
```

---

## Key Extraction Patterns

### UPI Patterns Detected
- `victim123@icici`
- `scammer@okhdfcbank`
- `lucky@paytm`
- `name@upi`

### Phone Patterns Detected
- `+919876543210`
- `09876543210`
- `9876543210`
- `+91-98765-43210`

### Link Patterns Detected
- `http://malicious-site.com`
- `https://bank-verify.in/kyc`
- `www.fake-lottery.com`

### Suspicious Keywords
- Account-related: "block", "suspend", "account", "verify"
- Urgency: "urgent", "immediately", "now", "limited time"
- Identity: "kyc", "pan", "aadhar", "identity", "update"
- Payment: "upi", "transfer", "send", "payment", "debit card"

---

## Testing Tips

1. **Always include sessionId** - Different session IDs for different conversations
2. **Use proper timestamps** - Current epoch time in milliseconds
3. **Include metadata** - Helps with context and evaluation
4. **Test multi-turn** - At least 4 messages to trigger final report
5. **Vary scam types** - Test UPI, bank, phishing, fake offers

---

**Last Updated:** February 2026
