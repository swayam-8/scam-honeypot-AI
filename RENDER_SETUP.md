# 🚀 RENDER DEPLOYMENT - Complete Setup Guide

## What You Need to Do

```
1. ✅ Create .env locally
2. ✅ Get API keys
3. ✅ Push code to GitHub
4. ✅ Deploy on Render.com
5. ✅ Provide URL & API key to GUVI
```

---

## Step 1: Create Local .env File

**Create file:** `a:\Skills\scam-honeypot-AI\.env`

**Content:**
```
GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
API_KEY=YOUR_SECRET_API_KEY_HERE
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

---

## Step 2: Get Your API Keys

### 🔑 Gemini API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Click "Get API Key"
3. Copy the generated key
4. Paste in `.env`:
   ```
   GEMINI_API_KEY=abc123defg456...
   ```

### 🔐 Secret API Key

Run in terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output:
```
AbCdEf_GhIjKlMnOpQrStUvWxYz-0123456789abcdefghij
```

Paste in `.env`:
```
API_KEY=AbCdEf_GhIjKlMnOpQrStUvWxYz-0123456789abcdefghij
```

---

## Step 3: Test Locally (Optional but Recommended)

```bash
# Navigate to project
cd a:\Skills\scam-honeypot-AI

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

Should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test in another terminal:
```bash
curl http://localhost:8000/
```

---

## Step 4: Push to GitHub

```bash
cd a:\Skills\scam-honeypot-AI

# Add all files
git add .

# Commit
git commit -m "Render deployment ready"

# Push
git push origin main
```

✅ Code is now on GitHub (WITHOUT .env - it's in .gitignore)

---

## Step 5: Deploy on Render.com

### 5a. Sign Up & Connect
- Go to https://render.com
- Sign up with GitHub
- Authorize Render to access your repos

### 5b. Create Web Service
1. Click "+ New"
2. Select "Web Service"
3. Select `scam-honeypot-AI` repository
4. Click "Connect"

### 5c. Configure Service
Fill in these fields:

| Field | Value |
|-------|-------|
| Name | `scam-honeypot-api` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python main.py` |
| Plan | `Free` |

### 5d. Add Environment Variables
Click "Advanced" and add:

**Variable 1:**
- Key: `GEMINI_API_KEY`
- Value: *Paste your Gemini API key*
- Click "Add"

**Variable 2:**
- Key: `API_KEY`
- Value: *Paste your generated secret key*
- Click "Add"

**Variable 3:**
- Key: `HOST`
- Value: `0.0.0.0`
- Click "Add"

**Variable 4:**
- Key: `PORT`
- Value: `8000`
- Click "Add"

**Variable 5:**
- Key: `RELOAD`
- Value: `false`
- Click "Add"

### 5e. Deploy
Click "Create Web Service"

⏳ Wait 2-5 minutes...

✅ When you see "Live", it's deployed!

---

## Step 6: Get Your Deployed URL

On Render dashboard, you'll see:

```
https://scam-honeypot-api.onrender.com
```

(Your actual service name will be different)

This is your **Endpoint URL** for GUVI

---

## Step 7: Verify Deployment Works

### Test Health Check
```bash
curl https://your-service-name.onrender.com/
```

Expected:
```json
{"Service Status": "HoneyPot Active & Waiting"}
```

### Test with API Key
```bash
curl -X POST https://your-service-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked",
      "timestamp": 1707000000000
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
  }'
```

Expected:
```json
{
  "status": "success",
  "reply": "Why will my account be blocked? What should I do?"
}
```

---

## 📝 What to Provide to GUVI

In GUVI's API tester platform, enter:

**Endpoint URL:**
```
https://your-service-name.onrender.com/chat
```

**API Key (x-api-key):**
```
YOUR_SECRET_API_KEY_HERE
```

Example:
```
Endpoint: https://scam-honeypot-api.onrender.com/chat
API Key: AbCdEf_GhIjKlMnOpQrStUvWxYz-0123456789abcdefghij
```

---

## 🔍 Monitor Your Deployment

On Render dashboard:
1. Click your service
2. Click "Logs" tab
3. See real-time requests and responses

---

## ⚠️ Troubleshooting

### Issue: Service shows "Build Failed"
**Solution:**
- Check build logs (click service, then "Logs")
- Usually missing dependency
- Verify requirements.txt is complete

### Issue: 401 Unauthorized when testing
**Solution:**
- Verify `API_KEY` is set in Render environment
- Use header: `x-api-key: your_actual_key`
- Check for typos

### Issue: 500 Server Error
**Solution:**
- Check logs on Render
- Usually `GEMINI_API_KEY` is invalid or missing
- Verify key is correct at aistudio.google.com

### Issue: Timeout when calling
**Solution:**
- Gemini API responses can be slow
- Render's free tier has limitations
- Consider upgrading to Starter plan ($7/month)

---

## 📱 Auto-Updates on Render

Whenever you push code to GitHub:
```bash
git push origin main
```

Render automatically:
1. Detects the push
2. Rebuilds
3. Redeploys

No manual action needed!

---

## ✅ Deployment Checklist

- [ ] Created local .env file
- [ ] Got Gemini API key
- [ ] Generated secret API key
- [ ] Tested locally (optional)
- [ ] Pushed code to GitHub
- [ ] Created Render web service
- [ ] Added all 5 environment variables
- [ ] Deployed successfully
- [ ] Service shows "Live"
- [ ] Health check works (GET /)
- [ ] API endpoint works (POST /chat)
- [ ] Ready to provide to GUVI

---

## 🎯 Summary

**What you're doing:**
1. Creating `.env` with your keys locally
2. Pushing code to GitHub (WITHOUT .env)
3. On Render, pasting the keys into environment variables
4. Render builds and deploys automatically
5. You get a public URL to give GUVI

**Files created for you:**
- `.env.example` - Template to copy
- `main.py` - Updated to use environment variables
- `render.yaml` - Automatic Render configuration
- `Procfile` - Deployment configuration
- `LOCAL_SETUP.md` - Local setup guide
- `QUICK_RENDER_SETUP.md` - 5-minute quick guide
- `RENDER_DEPLOYMENT.md` - Detailed guide

---

## 🚀 Ready to Deploy?

1. **Follow** [LOCAL_SETUP.md](LOCAL_SETUP.md) for local setup
2. **Follow** [QUICK_RENDER_SETUP.md](QUICK_RENDER_SETUP.md) for Render
3. **Provide** URL + API key to GUVI

**That's it!** Your API will be tested by GUVI's platform.

---

**Status**: ✅ Everything ready for Render deployment!
