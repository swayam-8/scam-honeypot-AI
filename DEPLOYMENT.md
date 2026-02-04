# Deployment & Setup Guide

Complete guide to deploy the Agentic Honey-Pot system to production.

## Prerequisites

- Python 3.8+
- Google Gemini API key
- Deployment platform (Render, Heroku, AWS, etc.)
- Git

## Local Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd scam-honeypot-AI
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env` file in project root:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
API_KEY=your_secret_api_key_here
```

### 5. Run Locally
```bash
python main.py
```

API will be available at: `http://localhost:8000`

### 6. Test the API
```bash
python test_api.py
```

---

## Production Deployment

### Option 1: Render.com (Recommended)

#### Step 1: Create Render Account
1. Sign up at https://render.com
2. Connect your GitHub account

#### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Select your GitHub repository
3. Configure:
   - **Name**: scam-honeypot-api
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: Free (or Starter for production)

#### Step 3: Set Environment Variables
1. Go to "Environment"
2. Add variables:
   ```
   GEMINI_API_KEY=your_key_here
   API_KEY=your_secret_key_here
   ```
3. Save and redeploy

#### Step 4: Verify Deployment
```bash
curl https://your-app-name.onrender.com/
# Should return: {"Service Status": "HoneyPot Active & Waiting"}
```

---

### Option 2: Heroku

#### Step 1: Create Heroku App
```bash
heroku login
heroku create scam-honeypot-api
```

#### Step 2: Set Environment Variables
```bash
heroku config:set GEMINI_API_KEY=your_key_here
heroku config:set API_KEY=your_secret_key_here
```

#### Step 3: Deploy
```bash
git push heroku main
```

#### Step 4: Monitor
```bash
heroku logs --tail
```

---

### Option 3: AWS (ECS)

#### Step 1: Create Docker Image
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

#### Step 2: Build Image
```bash
docker build -t scam-honeypot:latest .
```

#### Step 3: Push to ECR
```bash
aws ecr create-repository --repository-name scam-honeypot
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag scam-honeypot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/scam-honeypot:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/scam-honeypot:latest
```

#### Step 4: Create ECS Task & Service
Use AWS Console or CLI to create:
- Task Definition
- ECS Service
- Load Balancer (optional)

---

## Configuration Files

### requirements.txt
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
google-generativeai==0.3.0
httpx==0.25.1
```

### Procfile (for Heroku/Render)
```
web: python main.py
```

### Runtime.txt
```
python-3.11.7
```

---

## Environment Variables

### Required
```
GEMINI_API_KEY          # Google Gemini API key
API_KEY                 # Your secret API key for authentication
```

### Optional
```
LOG_LEVEL=INFO          # Logging level (DEBUG, INFO, WARNING, ERROR)
REPORT_ENDPOINT=...     # Custom GUVI endpoint (if different)
SESSION_TIMEOUT=3600    # Session timeout in seconds
```

---

## API Key Generation

### Generate a Secure API Key

**Option 1: Using Python**
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(f"API_KEY={api_key}")
```

**Option 2: Using OpenSSL**
```bash
openssl rand -base64 32
```

**Option 3: Using UUID**
```python
import uuid
api_key = str(uuid.uuid4())
print(f"API_KEY={api_key}")
```

---

## Monitoring & Logging

### Log Levels
- **DEBUG**: Detailed info for debugging
- **INFO**: General information (default)
- **WARNING**: Warning messages
- **ERROR**: Error messages only

### View Logs

**Render:**
```bash
# Via dashboard or
curl https://api.render.com/v1/services/<service-id>/logs
```

**Heroku:**
```bash
heroku logs --tail
```

**Local:**
```bash
# Logs are printed to console
tail -f application.log
```

### Important Log Markers
- 🔻🔻🔻 Incoming Request
- 📥 Incoming Request (structured)
- 🚀 Sending Final Report
- ✅ Success markers
- ❌ Error markers

---

## Health Checks

### Endpoint Health
```bash
curl https://your-api.com/
# Response: {"Service Status": "HoneyPot Active & Waiting"}
```

### API Health Check
```python
import requests

response = requests.post(
    "https://your-api.com/chat",
    json={"sessionId": "health-check", "message": None},
    headers={"x-api-key": "your-api-key"},
    timeout=10
)

if response.status_code == 200:
    print("✅ API is healthy")
else:
    print(f"❌ API returned {response.status_code}")
```

---

## Database Considerations

Current implementation uses in-memory storage (suitable for:
- Development
- Short-lived sessions
- Hobby projects

For production with persistence:

### Option 1: Redis (Recommended)
```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Store session
redis_client.set(f"session:{session_id}", json.dumps(session_data))

# Retrieve session
session_data = json.loads(redis_client.get(f"session:{session_id}"))
```

### Option 2: PostgreSQL
```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@localhost/honeypot"
engine = create_engine(DATABASE_URL)

# Create models and use SQLAlchemy ORM
```

### Option 3: MongoDB
```python
from pymongo import MongoClient

client = MongoClient("mongodb+srv://user:pass@cluster.mongodb.net")
db = client["honeypot"]
sessions = db["sessions"]

# Store session
sessions.insert_one(session_data)
```

---

## Performance Optimization

### 1. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat_handler(...):
    pass
```

### 2. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_session(session_id: str):
    return sessions.get(session_id)
```

### 3. Async Optimization
```python
# Already using async/await in the code
# Uvicorn with multiple workers:
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

---

## Security Hardening

### 1. API Key Security
```python
# Always use environment variables
api_key = os.environ.get("API_KEY")

# Rotate keys regularly
# Never commit keys to git
```

### 2. CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hackathon.guvi.in"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "x-api-key"],
)
```

### 3. Request Validation
```python
# Pydantic models already validate
# Add max payload size
# Sanitize user inputs
```

### 4. HTTPS Only
```python
# Ensure production uses HTTPS
# Render/Heroku handle this automatically
# For custom deployments: use Let's Encrypt + nginx
```

---

## Troubleshooting Deployment

### Issue: API Not Responding
**Solution:**
1. Check if service is running: `curl https://your-api.com/`
2. Check logs for errors
3. Verify environment variables are set
4. Ensure API key is correct

### Issue: "GEMINI_API_KEY not found"
**Solution:**
1. Verify API key is set in environment variables
2. Check spelling: `GEMINI_API_KEY` (exact case)
3. Redeploy after setting variables
4. Restart service

### Issue: Slow Responses (>30s)
**Solution:**
1. Gemini API may be slow: increase timeout
2. Check network connectivity
3. Scale up instance type
4. Add response caching

### Issue: "Report not being sent"
**Solution:**
1. Check if 4+ messages were exchanged
2. Verify extracted intelligence
3. Check GUVI endpoint connectivity
4. Review logs for errors

---

## Continuous Integration/Deployment (CI/CD)

### GitHub Actions Example
```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl -X POST https://api.render.com/deploy/srv-xxxxx \
            -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}"
```

---

## Backup & Recovery

### Data Export
```python
# Export session data
import json

with open("backup_sessions.json", "w") as f:
    json.dump(sessions, f, indent=2)
```

### Session Recovery
```python
# Restore from backup
import json

with open("backup_sessions.json", "r") as f:
    sessions = json.load(f)
```

---

## Capacity Planning

### Expected Load
- 100 messages/hour: Free tier sufficient
- 1,000 messages/hour: Starter tier recommended
- 10,000+ messages/hour: Scale tier or custom infrastructure

### Resource Requirements
- **Memory**: 256MB minimum (512MB recommended)
- **CPU**: Shared tier sufficient
- **Network**: 100GB/month typical usage

---

## Compliance & Regulations

✅ **Data Protection**
- GDPR compliant (no PII storage for non-evaluation)
- Secure API key handling
- No credential exposure in logs

⚠️ **Important**
- This is a honeypot - only engage with actual scammers
- Don't target legitimate users
- Comply with local regulations
- Ethical use only

---

**Last Updated:** February 2026  
**Status:** Production Ready
