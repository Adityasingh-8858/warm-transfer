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

@app.get("/get-token")
async def get_token(room_name: str, identity: str) -> TokenResponse:
    """
    Generate a LiveKit access token for a client.
    
    Args:
        room_name: The name of the room to join
        identity: The identity/name of the participant
    
    Returns:
        TokenResponse containing the access token
    """
    try:
        # Create access token with room join permissions
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(identity) \
            .with_name(identity) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            ))
        
        access_token = token.to_jwt()
        logger.info(f"Generated token for {identity} in room {room_name}")
        
        return TokenResponse(accessToken=access_token)
    
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate access token")

@app.post("/initiate-transfer")
async def initiate_transfer(request: TransferRequest) -> TransferResponse:
    """
    Start the transfer process by generating a call summary using Groq LLM.
    
    Args:
        request: TransferRequest containing call_context
    
    Returns:
        TransferResponse containing the generated summary
    """
    try:
        # Call Groq API to generate summary
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise summaries of customer service calls. "
                              "Your summary should include the customer's main issue, any progress made, "
                              "and what still needs to be resolved. Keep it under 200 words."
                },
                {
                    "role": "user", 
                    "content": f"Please summarize this call context for a warm transfer: {request.call_context}"
                }
            ],
            model="llama3-8b-8192",  # Using a fast Groq model
            temperature=0.3,
            max_tokens=300
        )
        
        summary = chat_completion.choices[0].message.content
        logger.info("Generated call summary for transfer")
        
        return TransferResponse(summary=summary)
    
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate call summary")

@app.post("/complete-transfer")
async def complete_transfer(request: CompleteTransferRequest) -> SuccessResponse:
    """
    Complete the transfer by removing Agent A from the original room
    and ensuring Agent B can join.
    
    Args:
        request: CompleteTransferRequest with room and agent details
    
    Returns:
        SuccessResponse confirming the transfer completion
    """
    try:
        # Remove Agent A from the original room
        await livekit_api.room.remove_participant(
            api.RemoveParticipantRequest(
                room=request.original_room_name,
                identity=request.agent_a_identity
            )
        )
        
        logger.info(f"Removed {request.agent_a_identity} from room {request.original_room_name}")
        
        # Note: Agent B joining is handled by the frontend generating a new token
        # for the original room. The room will now contain only the caller and Agent B.
        
        return SuccessResponse(
            success=True, 
            message=f"Transfer completed. {request.agent_a_identity} removed from {request.original_room_name}"
        )
    
    except Exception as e:
        logger.error(f"Error completing transfer: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete transfer")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)