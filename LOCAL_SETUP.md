# 📋 Setup Instructions - Before Deploying to Render

## 1. Create Your .env File Locally

```bash
cd a:\Skills\scam-honeypot-AI
```

Copy the template:
```bash
copy .env.example .env
```

Or manually create `.env` with:
```
GEMINI_API_KEY=your_gemini_api_key_here
API_KEY=your_secret_api_key_here
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

---

## 2. Get Your API Keys

### Google Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Click "Get API Key"
3. Copy the key
4. Paste into `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

### Generate Your Secret API Key
Run this command:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste into `.env`:
```
API_KEY=your_generated_key_here
```

---

## 3. Test Locally First

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it:
```bash
# In another terminal
curl http://localhost:8000/
```

Response should be:
```json
{"Service Status": "HoneyPot Active & Waiting"}
```

---

## 4. Prepare for Render Deployment

**IMPORTANT**: The .env file is in .gitignore and will NOT be pushed to GitHub.

On Render, you'll paste the keys directly into their environment variable dashboard.

---

## 5. Push Code to GitHub

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

---

## 6. Deploy on Render.com

Follow: [QUICK_RENDER_SETUP.md](QUICK_RENDER_SETUP.md)

Or detailed: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

---

## Summary

```
✅ Local .env created (for local testing)
✅ Code pushed to GitHub (without .env - it's in .gitignore)
✅ Ready to deploy on Render (paste keys in Render dashboard)
```

Next: Follow [QUICK_RENDER_SETUP.md](QUICK_RENDER_SETUP.md) to deploy!
