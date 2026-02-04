# 🎯 Quick Render Deployment (5 Minutes)

## What You'll Get After Deployment

```
Your Endpoint URL: https://your-service-name.onrender.com/chat
Your API Key: abc123xyz789...
```

→ Use these with GUVI's API tester

---

## 5-Minute Setup

### 1️⃣ **Prepare Keys** (1 min)

**Get Gemini API Key:**
- Go to https://aistudio.google.com/app/apikey
- Click "Get API Key"
- Copy the key
- Save it (you'll paste it in Render)

**Generate Your API Key:**
```bash
# Run in terminal
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
- Copy the output
- Save it (you'll paste it in Render)

---

### 2️⃣ **Push to GitHub** (1 min)

```bash
cd a:\Skills\scam-honeypot-AI
git add .
git commit -m "Render deployment"
git push origin main
```

✅ Code is now on GitHub

---

### 3️⃣ **Deploy on Render** (3 min)

**Go to:** https://render.com

**Step A: Create Web Service**
- Click "+ New"
- Select "Web Service"
- Select your GitHub repo
- Click "Connect"

**Step B: Configure**
- Name: `scam-honeypot-api`
- Build: `pip install -r requirements.txt`
- Start: `python main.py`
- Plan: `Free`

**Step C: Environment Variables**
Click "Advanced" → Add these:

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | *paste your Gemini key* |
| `API_KEY` | *paste your generated key* |
| `HOST` | `0.0.0.0` |
| `PORT` | `8000` |
| `RELOAD` | `false` |

**Step D: Deploy**
- Click "Create Web Service"
- Wait 2-5 minutes
- You'll see: ✅ **Live**

---

## ✅ Your URLs Are Ready

**Endpoint URL:**
```
https://scam-honeypot-api.onrender.com/chat
```

**API Key (keep secret):**
```
your_generated_secret_key_here
```

---

## 🎯 Provide to GUVI

On GUVI's platform, enter:

```
Endpoint: https://scam-honeypot-api.onrender.com/chat
API Key: your_generated_secret_key_here
```

That's it! GUVI will test your API automatically.

---

## 🔍 How to Check Logs

On Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. See real-time activity

---

## ⚡ Quick Troubleshooting

| Problem | Fix |
|---------|-----|
| 401 Unauthorized | Check API_KEY is set in Render env |
| 500 Error | Check GEMINI_API_KEY is valid |
| Won't start | Check build logs for errors |
| Timeout | Wait, Render's free tier is slower |

---

## ✨ You're Done!

Your API is now publicly accessible at:
```
https://your-service.onrender.com
```

Ready to submit to GUVI! 🚀

---

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions.
