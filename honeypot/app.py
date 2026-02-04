from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from honeypot.routers import chat

app = FastAPI(
    title="Scam HoneyPot AI",
    description="AI-powered scam detection and intelligence extraction",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
def home():
    return {
        "status": "active",
        "service": "HoneyPot AI",
        "message": "HoneyPot is active and waiting for scam messages"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
