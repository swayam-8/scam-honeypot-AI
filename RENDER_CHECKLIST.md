# 🎯 Render Deployment - Quick Checklist

## Before You Start

- [ ] GitHub account
- [ ] Render.com account (sign up free)
- [ ] Google Gemini API key ready (from aistudio.google.com)

---

## Phase 1: Prepare Keys (5 minutes)

### Get Gemini API Key
- [ ] Go to https://aistudio.google.com/app/apikey
- [ ] Click "Get API Key"
- [ ] Copy the key
- [ ] Save somewhere safe

### Generate Secret API Key
- [ ] Open terminal in `a:\Skills\scam-honeypot-AI`
- [ ] Run: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Copy the output
- [ ] Save somewhere safe

---

## Phase 2: Create Local .env (2 minutes)

- [ ] Create file: `a:\Skills\scam-honeypot-AI\.env`
- [ ] Add:
  ```
  GEMINI_API_KEY=<paste_your_gemini_key>
  API_KEY=<paste_your_secret_key>
  HOST=0.0.0.0
  PORT=8000
  RELOAD=true
  ```
- [ ] Save file

---

## Phase 3: Test Locally (Optional - 3 minutes)

- [ ] Run: `pip install -r requirements.txt`
- [ ] Run: `python main.py`
- [ ] In another terminal: `curl http://localhost:8000/`
- [ ] Should see: `{"Service Status": "HoneyPot Active & Waiting"}`
- [ ] Press Ctrl+C to stop

---

## Phase 4: Push to GitHub (2 minutes)

- [ ] Run: `git add .`
- [ ] Run: `git commit -m "Ready for Render"`
- [ ] Run: `git push origin main`
- [ ] Verify on GitHub - code is there (but NO .env file)

---

## Phase 5: Deploy on Render (5 minutes)

### Create Web Service
- [ ] Go to https://render.com
- [ ] Click "+ New"
- [ ] Select "Web Service"
- [ ] Select your `scam-honeypot-AI` repo
- [ ] Click "Connect"

### Configure
- [ ] Name: `scam-honeypot-api`
- [ ] Build: `pip install -r requirements.txt`
- [ ] Start: `python main.py`
- [ ] Plan: `Free`

### Add Environment Variables
- [ ] Click "Advanced"
- [ ] Add `GEMINI_API_KEY` = *your Gemini key*
- [ ] Add `API_KEY` = *your secret key*
- [ ] Add `HOST` = `0.0.0.0`
- [ ] Add `PORT` = `8000`
- [ ] Add `RELOAD` = `false`

### Deploy
- [ ] Click "Create Web Service"
- [ ] ⏳ Wait 2-5 minutes for build
- [ ] ✅ When green "Live", it's deployed!

---

## Phase 6: Verify & Get URL (3 minutes)

### Get Your Endpoint
- [ ] On Render dashboard, copy the service URL
- [ ] Format: `https://your-service-name.onrender.com`

### Test Health Check
- [ ] Run: `curl https://your-service-name.onrender.com/`
- [ ] Should see: `{"Service Status": "HoneyPot Active & Waiting"}`

### Test API Endpoint
```bash
curl -X POST https://your-service-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_SECRET_KEY" \
  -d '{"sessionId":"test","message":{"sender":"scammer","text":"Your account blocked","timestamp":1707000000000},"conversationHistory":[],"metadata":{"channel":"SMS","language":"English","locale":"IN"}}'
```
- [ ] Should see response with status: `success`

---

## Phase 7: Provide to GUVI (1 minute)

Write down these values:

**Endpoint URL:**
```
https://your-service-name.onrender.com/chat
```

**API Key:**
```
YOUR_SECRET_API_KEY_HERE
```

- [ ] Enter these in GUVI's API tester
- [ ] GUVI will test your API automatically

---

## ✅ All Done!

Your API is:
- ✅ Deployed on Render
- ✅ Running publicly
- ✅ Ready for GUVI testing

---

## 📚 Helpful Guides

- **Quick Setup (5 min)**: [QUICK_RENDER_SETUP.md](QUICK_RENDER_SETUP.md)
- **Detailed Steps**: [RENDER_SETUP.md](RENDER_SETUP.md)
- **Local Testing**: [LOCAL_SETUP.md](LOCAL_SETUP.md)

---

## 🆘 Need Help?

| Issue | Check |
|-------|-------|
| Don't have Gemini key | https://aistudio.google.com/app/apikey |
| Can't generate API key | Run: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| Service won't start | Check Render logs (Logs tab) |
| 401 error | Verify API_KEY in Render environment |
| 500 error | Check if GEMINI_API_KEY is valid |

---

## ⏱️ Total Time Needed

```
Prepare keys:      5 min
Create .env:       2 min
Test locally:      3 min (optional)
Push to GitHub:    2 min
Deploy on Render:  5 min
Verify & test:     3 min
─────────────────────────
Total:            20 min
```

---

**Status**: ✅ Everything ready!  
**Next**: Follow the phases above.  
**Time needed**: 20 minutes total

---

Go to [QUICK_RENDER_SETUP.md](QUICK_RENDER_SETUP.md) to get started! 🚀
