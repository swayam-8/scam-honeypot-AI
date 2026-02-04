from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <--- IMPORT THIS
from honeypot.routers import chat

app = FastAPI(title="Scam HoneyPot AI")

# --- ADD THIS SECTION TO FIX "INVALID_REQUEST_BODY" ON WEBSITE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL websites (including hackathon.guvi.in)
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],  # Allows x-api-key header
)
# -----------------------------------------------------------------

app.include_router(chat.router)

@app.get("/")
def home():
    return {"Service Status": "HoneyPot Active & Waiting"}