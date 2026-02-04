# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

A sophisticated AI-powered honeypot system that detects and engages scammers in multi-turn conversations to extract actionable intelligence.

## 🎯 Overview

This system implements an intelligent honeypot that:
- Detects scam intent in incoming messages
- Activates an AI agent to respond like a naive victim
- Maintains believable multi-turn conversations
- Extracts actionable intelligence (UPI IDs, phone numbers, bank details, phishing links)
- Sends comprehensive reports to the GUVI evaluation endpoint

## 🏗️ Architecture

```
honeypot/
├── AI.py              # AI Agent for conversation & scam analysis
├── app.py             # FastAPI application setup
├── store.py           # Session & conversation storage
├── utils.py           # Intelligence extraction & analysis
└── routers/
    └── chat.py        # Main API endpoint handler
```

### Core Components

#### 1. **AI.py** - Intelligent Agent
- Multi-turn conversation handling
- Scam intent detection using Gemini 2.5 Flash
- Human-like victim persona
- Adaptive responses based on conversation history
- Confidence scoring for scam detection

**Key Features:**
- Analyzes conversation context
- Generates natural, human-like responses
- Avoids revealing detection
- Requests specific intelligence

#### 2. **chat.py** - API Endpoint
- Accepts incoming scam messages
- Manages authentication (x-api-key header)
- Routes messages to AI agent
- Triggers final report when conditions are met
- Implements background task for report delivery

**Endpoint:** `POST /chat`

#### 3. **store.py** - Session Management
- Maintains conversation state across messages
- Tracks extracted intelligence
- Manages message history
- Determines when to send final reports
- Prevents duplicate reporting

#### 4. **utils.py** - Intelligence Extraction
- Extracts UPI IDs (e.g., `scammer@okhdfcbank`)
- Detects phone numbers (Indian format)
- Identifies phishing links
- Extracts bank account numbers
- Identifies suspicious keywords
- Heuristic scam likelihood scoring

## 📡 API Specification

### Request Format

```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked...",
    "timestamp": 1770005528731
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Previous message...",
      "timestamp": 1770005528700
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response Format

```json
{
  "status": "success",
  "reply": "AI agent's response to scammer"
}
```

### Authentication

Provide API key via header:
```
x-api-key: YOUR_SECRET_API_KEY
```

## 🤖 Agent Behavior

### Persona
- Naive, non-tech-savvy victim (elderly person)
- Emotional and worried
- Willing to comply but slightly confused
- Natural, casual language
- Short, message-like responses (1-3 sentences)

### Engagement Strategy
1. **Listen** - Process scammer's intent
2. **Ask** - Request clarification to extract details
3. **Comply** - Appear willing to follow instructions
4. **Waste Time** - Extend conversation for intelligence gathering
5. **Extract** - Naturally encourage sharing of sensitive information

### Example Flow

**Scammer:** "Your UPI needs verification. Share your ID."  
**Agent:** "I'm scared! What will happen if I don't? I use paytm, is that okay?"

**Scammer:** "No, use your bank UPI. Send it now!"  
**Agent:** "OK, I have ICICI bank. Is it scammer@icici or something else?"

## 📊 Intelligence Extraction

The system automatically extracts:

### Financial Information
- **UPI IDs**: `victim@icici`, `name@okhdfcbank`
- **Bank Accounts**: 12-16 digit numbers with account patterns
- **Phone Numbers**: Indian format (+91, 0-prefix, 10-digit)

### Threat Indicators
- **Phishing Links**: HTTP/HTTPS/WWW URLs
- **Suspicious Keywords**: "urgent", "verify", "block", "suspend", "kyc", "OTP", etc.

## 📋 Final Report Trigger

Reports are sent to the GUVI endpoint when:
- **4+ messages exchanged**, OR
- **Critical intelligence found** (UPI/Bank/Phone) AND 2+ messages

### Report Payload

```json
{
  "sessionId": "abc123-session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 8,
  "extractedIntelligence": {
    "bankAccounts": ["123456789012"],
    "upiIds": ["scammer@okhdfcbank"],
    "phishingLinks": ["http://malicious-link.com"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "verify", "block", "kyc"]
  },
  "agentNotes": "Scammer used urgency tactics and requested UPI verification"
}
```

### Report Endpoint
```
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult
Content-Type: application/json
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key
API_KEY=your_secret_api_key
```

### Server Configuration

Edit `main.py`:
```python
uvicorn.run("honeypot.app:app", host="0.0.0.0", port=8000, reload=True)
```

## 🚀 Deployment

### Local Development
```bash
python main.py
```
API will be available at `http://localhost:8000`

### Production (Render/Heroku)
1. Set environment variables in platform dashboard
2. Ensure `Procfile` points to the correct entry point
3. API key must be configured on the platform

### Testing
```bash
python test_api.py
```

This runs comprehensive tests including:
- Ping requests
- Single message scams
- Multi-turn conversations
- Various scam types

## 📈 Evaluation Criteria

The system is evaluated on:
1. **Scam Detection Accuracy** - Correctly identifying fraudulent messages
2. **Agentic Engagement** - Maintaining believable conversation
3. **Intelligence Extraction** - Quality and completeness of extracted data
4. **API Stability** - Reliable responses and report delivery
5. **Ethical Behavior** - No impersonation, no illegal activity

## 🔐 Security & Ethics

✅ **Responsible Data Handling**
- Sanitized logging
- No credential exposure
- Secure API key verification

❌ **Prohibited Actions**
- No impersonation of real individuals
- No illegal instructions
- No harassment
- No unreliable targeting

## 📝 Conversation Flow Example

```
1. Scammer: "Your account will be blocked. Verify immediately."
2. Agent: "What? Why will it be blocked? I didn't do anything!"
3. Scammer: "Share your UPI ID to avoid suspension."
4. Agent: "OK, but I'm worried. My UPI is victim@icici. Will that fix it?"
5. Scammer: "Yes, now send ₹500 to reactivate."
6. Agent: "I'm scared to lose my account. Can I send through Google Pay instead?"
   
[After 4+ messages with intelligence extracted]
7. System sends final report to GUVI endpoint
```

## 🛠️ Troubleshooting

### "Connection Timeout"
- Ensure Gemini API is accessible
- Check internet connectivity
- Verify API key is valid

### "JSON Parse Error"
- AI model response may be malformed
- Fallback response automatically generated
- Check logs for details

### "Report Not Sent"
- Verify conversation has 4+ messages OR critical intelligence
- Check GUVI endpoint availability
- Ensure API key is set

## 📚 API Examples

### Example 1: Initial Scam Detection
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key" \
  -d '{
    "sessionId": "sess-001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Verify now at http://bank-verify.com",
      "timestamp": 1707000000000
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
  }'
```

### Example 2: Multi-Turn Engagement
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key" \
  -d '{
    "sessionId": "sess-001",
    "message": {
      "sender": "scammer",
      "text": "Share your UPI to reactivate: scammer@okhdfcbank",
      "timestamp": 1707000005000
    },
    "conversationHistory": [{
      "sender": "scammer",
      "text": "Your account is blocked",
      "timestamp": 1707000000000
    }],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
  }'
```

## 📞 Support & Monitoring

### Logs
- All requests logged with timestamp
- AI responses logged for analysis
- Report delivery status tracked
- Errors logged with full context

### Health Check
```bash
curl http://localhost:8000/
```
Response:
```json
{"Service Status": "HoneyPot Active & Waiting"}
```

## 🎓 Key Technologies

- **Framework**: FastAPI
- **AI Model**: Google Gemini 2.5 Flash
- **Server**: Uvicorn
- **Language**: Python 3.8+
- **Libraries**: httpx (async HTTP), pydantic (validation)

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Status**: Production Ready
