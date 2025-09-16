from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging
from livekit import api
from groq import Groq
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Warm Transfer API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables validation
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL, GROQ_API_KEY]):
    logger.error("Missing required environment variables")
    raise ValueError("Missing required environment variables")

# Initialize clients
livekit_api = api.LiveKitAPI(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
groq_client = Groq(api_key=GROQ_API_KEY)

# Pydantic models for request/response
class TokenRequest(BaseModel):
    room_name: str
    identity: str

class TokenResponse(BaseModel):
    accessToken: str

class TransferRequest(BaseModel):
    call_context: str

class TransferResponse(BaseModel):
    summary: str

class CompleteTransferRequest(BaseModel):
    original_room_name: str
    agent_a_identity: str
    agent_b_identity: str

class SuccessResponse(BaseModel):
    success: bool
    message: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Warm Transfer API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)