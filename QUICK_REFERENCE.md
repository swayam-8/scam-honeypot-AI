# Quick Reference Card

## API Endpoint

```
POST /chat
Host: your-api.com
Content-Type: application/json
x-api-key: YOUR_API_KEY
```

## Request Template
```json
{
  "sessionId": "unique-id",
  "message": {
    "sender": "scammer",
    "text": "The message content",
    "timestamp": 1707000000000
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS|WhatsApp|Email|Chat",
    "language": "English",
    "locale": "IN"
  }
}
```

## Response
```json
{
  "status": "success",
  "reply": "AI agent's response"
}
```

## Key Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `sessionId` | Unique conversation ID | `"sess-001"` |
| `sender` | Message source | `"scammer"` or `"user"` |
| `timestamp` | Epoch milliseconds | `1707000000000` |
| `channel` | Communication channel | `"SMS"`, `"WhatsApp"` |

## Final Report Trigger

**Condition:** 4+ messages OR critical intelligence  
**Endpoint:** `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`  
**Automatic:** Yes (background task)

## Extracted Intelligence Types

| Type | Pattern | Example |
|------|---------|---------|
| UPI IDs | `xxx@bank` | `scammer@okhdfcbank` |
| Phone | Indian format | `+919876543210` |
| Bank Account | 12-16 digits | `987654321012` |
| Phishing Links | URLs | `http://verify.com` |
| Keywords | Scam indicators | `"urgent"`, `"verify"` |

## Testing Checklist

- [ ] Ping test (empty message)
- [ ] Single scam message
- [ ] Multi-turn conversation (4+ messages)
- [ ] Final report callback
- [ ] Wrong API key (401 error)
- [ ] Various scam types

## Environment Setup

```bash
# 1. Create .env file
echo "GEMINI_API_KEY=your_key" > .env
echo "API_KEY=your_api_key" >> .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run locally
python main.py

# 4. Test
python test_api.py
```

## Deployment Commands

**Render:**
```bash
git push origin main  # Auto-deploys if connected
```

**Heroku:**
```bash
git push heroku main
```

**Local (Production):**
```bash
uvicorn honeypot.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Monitoring

```bash
# Health check
curl https://your-api.com/

# Test request
curl -X POST https://your-api.com/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-key" \
  -d '{
    "sessionId": "test",
    "message": {
      "sender": "scammer",
      "text": "Test message",
      "timestamp": 1707000000000
    },
    "conversationHistory": [],
    "metadata": {}
  }'
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Wrong API key | Check `x-api-key` header |
| 422 Validation Error | Bad request format | Check JSON structure |
| 500 Internal Server | AI error | Check Gemini API key |
| Report not sent | <4 messages | Continue conversation |

## File Structure

```
honeypot/
├── AI.py              # Agent logic
├── app.py             # FastAPI setup
├── store.py           # Session storage
├── utils.py           # Intelligence extraction
└── routers/
    └── chat.py        # Main endpoint
```

## Key Functions

```python
# AI.py
analyze_and_reply(text, history)  # Generate response

# utils.py
extract_intelligence(text)         # Extract UPI, phone, etc.
is_likely_scam(text)              # Quick scam check

# store.py
get_or_create_session(id)         # Get/create session
update_session(id, intel)         # Update with intelligence
should_send_report(id)            # Check if ready to report
mark_report_sent(id)              # Mark as reported
```

## Multi-Turn Conversation Flow

```
1. User → Scam message
   ↓
2. API → Detect scam intent
   ↓
3. AI → Generate victim-like response
   ↓
4. User → Next scammer message + history
   ↓
5. Repeat until 4+ messages or critical intel
   ↓
6. API → Send final report to GUVI
```

## Intelligence Extraction Examples

**Input:** "Your account blocked! Verify at bank123.com. Call +919876543210. Send UPI: scammer@okhdfcbank"

**Output:**
```json
{
  "phishingLinks": ["bank123.com"],
  "phoneNumbers": ["+919876543210"],
  "upiIds": ["scammer@okhdfcbank"],
  "suspiciousKeywords": ["account", "blocked", "verify"],
  "bankAccounts": []
}
```

## API Key Generation

```bash
# Option 1: Python secrets
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: OpenSSL
openssl rand -base64 32

# Option 3: UUID
python -c "import uuid; print(uuid.uuid4())"
```

## Rate Limiting (Optional)

Recommended limits:
- 10 requests/minute per API key
- 1000 requests/day per API key
- 100 concurrent sessions max

## Performance Metrics

Expected response times:
- Ping request: <100ms
- Scam detection: 2-5s (Gemini API)
- Final report: <5s (background task)

## Debugging Tips

1. **Check logs:** Look for 🔻 markers
2. **Test with curl:** Use test_api.py examples
3. **Validate JSON:** Use jsonlint.com
4. **API key:** Verify in environment variables
5. **Timestamps:** Use milliseconds (ms)

## Security Reminders

- ❌ Never commit `.env` to git
- ❌ Don't expose API key in logs
- ❌ Don't share API key in chat/email
- ✅ Rotate keys regularly
- ✅ Use HTTPS in production
- ✅ Validate all inputs

## Support Resources

- 📖 Full Docs: `IMPLEMENTATION.md`
- 🔗 API Examples: `API_EXAMPLES.md`
- 🚀 Deployment: `DEPLOYMENT.md`
- 🧪 Tests: `test_api.py`

---

**Version:** 1.0  
**Updated:** February 2026
