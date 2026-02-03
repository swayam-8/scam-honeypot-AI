from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- CRITICAL IMPORT
from honeypot.routers import chat

app = FastAPI(title="Scam HoneyPot AI")

# --- ENABLE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL websites
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

app.include_router(chat.router)

@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {"Service Status": "HoneyPot Active & Waiting"}