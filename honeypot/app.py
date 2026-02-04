from fastapi import FastAPI
from honeypot.routers import chat

app = FastAPI(title="Scam HoneyPot AI")

app.include_router(chat.router)

@app.get("/")
def home():
    return {"Service Status": "HoneyPot Active & Waiting"}