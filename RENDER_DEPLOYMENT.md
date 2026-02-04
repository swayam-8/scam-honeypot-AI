# 🚀 Render.com Deployment Guide

## Step-by-Step Instructions for Deploying to Render.com

### Prerequisites
- GitHub account with your code pushed
- Render.com account (sign up at https://render.com)
- Google Gemini API key
- Generated API key for authentication

---

## Step 1: Push Code to GitHub

```bash
cd a:\Skills\scam-honeypot-AI

# Initialize git if not done
git init
git add .
git commit -m "Initial commit - Scam HoneyPot AI"

# Push to GitHub
git push origin main
```

**Note**: Make sure `.env` is in `.gitignore` (it should be)

---

## Step 2: Create Render Account & Connect GitHub

1. Go to https://render.com
2. Click "Sign up"
3. Connect with GitHub
4. Authorize Render to access your repositories

---

## Step 3: Create New Web Service on Render

1. Click **"New +"** button
2. Select **"Web Service"**
3. Connect your GitHub repository
4. Select the **scam-honeypot-AI** repository

---

## Step 4: Configure Service Settings

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `scam-honeypot-api` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python main.py` |
| **Plan** | `Free` (or Starter if you need more) |

---

## Step 5: Add Environment Variables

Click on **"Environment"** tab

**Add these variables:**

1. **GEMINI_API_KEY**
   - Click "Add Environment Variable"
   - Key: `GEMINI_API_KEY`
   - Value: `your_actual_gemini_api_key_here`
   - Click "Add"

2. **API_KEY**
   - Click "Add Environment Variable"
   - Key: `API_KEY`
   - Value: `your_generated_secret_api_key_here`
   - Click "Add"

3. **HOST**
   - Key: `HOST`
   - Value: `0.0.0.0`

4. **PORT**
   - Key: `PORT`
   - Value: `8000`

5. **RELOAD**
   - Key: `RELOAD`
   - Value: `false`

---

## Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait for build to complete (2-5 minutes)
3. Check the logs for any errors

**Your service URL will be displayed:**
```
https://scam-honeypot-api.onrender.com
```

(Your actual name will be different)

---

## Step 7: Verify Deployment

### Test Health Check
```bash
curl https://your-service-name.onrender.com/
```

**Expected response:**
```json
{"Service Status": "HoneyPot Active & Waiting"}
```

### Test API Endpoint
```bash
curl -X POST https://your-service-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key" \
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

**Expected response:**
```json
{
  "status": "success",
  "reply": "Why will my account be blocked? What should I do?"
}
```

---

## 📝 What to Provide to GUVI

Once deployed, provide GUVI with:

**Endpoint URL:**
```
https://your-service-name.onrender.com/chat
```

**API Key (x-api-key):**
```
your_generated_secret_api_key_here
```

---

## 📊 View Logs on Render

1. Go to your service dashboard
2. Click **"Logs"** tab
3. See real-time requests and responses
4. Check for errors

---

## ⚠️ Common Issues

### Issue: 401 Unauthorized
**Solution**: 
- Verify API_KEY is set in environment variables
- Check spelling: `x-api-key` (lowercase)
- Redeploy after changing env vars

### Issue: 500 Server Error
**Solution**:
- Check logs: Click "Logs" tab
- Usually means GEMINI_API_KEY is missing or invalid
- Verify the key is correct at aistudio.google.com

### Issue: Timeout
**Solution**:
- Gemini API may be slow initially
- Render's free tier has limitations
- Consider upgrading to Starter plan

### Issue: Service Won't Start
**Solution**:
- Check build logs
- Usually missing dependencies
- Verify requirements.txt is complete

---

## 🔄 Updating Your Code

When you make changes:

```bash
git add .
git commit -m "Update description"
git push origin main
```

Render automatically redeploys!

---

## 💾 Environment Variables on Render

**Important**: Always set sensitive keys directly in Render dashboard, never in code!

To update later:
1. Go to service settings
2. Click "Environment"
3. Update the values
4. Service auto-restarts with new values

---

## 📱 Alternative: Using render.yaml

If you want automatic deployment configuration:

The `render.yaml` file in your repo contains all settings. Render will read it and auto-configure your service.

To use:
1. On Render, click "Infrastructure as Code"
2. Select your repo
3. Click "Deploy"
4. It will use settings from render.yaml

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] GitHub connected to Render
- [ ] Web Service created
- [ ] GEMINI_API_KEY added to environment
- [ ] API_KEY added to environment
- [ ] HOST, PORT, RELOAD configured
- [ ] Service deployed successfully
- [ ] Health check works (GET /)
- [ ] API endpoint works (POST /chat)
- [ ] Logs show no errors
- [ ] Ready to provide to GUVI

---

## 🎯 Summary

**3 Easy Steps:**
1. Push to GitHub
2. Connect to Render
3. Add environment variables
4. Deploy!

**Your deployed URL:** `https://scam-honeypot-api.onrender.com` (example)
**Your API Key:** `your_secret_api_key_here`

---

**Status**: ✅ Ready for GUVI submission!
