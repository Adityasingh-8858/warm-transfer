from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging
import time
from groq import Groq
from livekit import api
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info("Starting Warm Transfer API")
    yield
    # Shutdown
    global livekit_api
    if livekit_api:
        await livekit_api.aclose()
        logger.info("Closed LiveKit API client")

# Initialize FastAPI app with lifespan
app = FastAPI(title="Warm Transfer API", version="1.0.0", lifespan=lifespan)

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

if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL]):
    logger.error("Missing required LiveKit environment variables")
    raise ValueError("Missing required LiveKit environment variables: LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL")

# Initialize clients
groq_client = None  # Will be initialized when needed
livekit_api = None  # Will be initialized when needed

def get_livekit_api():
    """Get LiveKit API client instance"""
    global livekit_api
    if livekit_api is None:
        livekit_api = api.LiveKitAPI(LIVEKIT_URL)
    return livekit_api

def create_livekit_token(room_name: str, identity: str, name: str | None = None) -> str:
    """
    Create a LiveKit access token using the official SDK
    """
    try:
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(identity) \
            .with_name(name or identity) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )).to_jwt()
        
        return token
    except Exception as e:
        logger.error(f"Error creating LiveKit token: {str(e)}")
        raise

async def create_room_if_not_exists(room_name: str):
    """
    Create a room if it doesn't already exist
    """
    try:
        lk_api = get_livekit_api()
        
        # Try to create the room
        room_info = await lk_api.room.create_room(
            api.CreateRoomRequest(name=room_name)
        )
        logger.info(f"Created room: {room_name}")
        return room_info
        
    except Exception as e:
        # Room might already exist, which is fine
        logger.info(f"Room {room_name} may already exist or creation failed: {str(e)}")
        return None

async def list_rooms():
    """
    List all active rooms
    """
    try:
        lk_api = get_livekit_api()
        result = await lk_api.room.list_rooms(api.ListRoomsRequest())
        return result.rooms
    except Exception as e:
        logger.error(f"Error listing rooms: {str(e)}")
        return []

async def remove_participant_from_room(room_name: str, identity: str):
    """
    Remove a participant from a room (for transfer completion)
    """
    try:
        lk_api = get_livekit_api()
        # This requires finding the participant first
        participants = await lk_api.room.list_participants(
            api.ListParticipantsRequest(room=room_name)
        )
        
        # Find the participant by identity
        target_participant = None
        for participant in participants.participants:
            if participant.identity == identity:
                target_participant = participant
                break
        
        if target_participant:
            await lk_api.room.remove_participant(
                api.RoomParticipantIdentity(
                    room=room_name,
                    identity=identity
                )
            )
            logger.info(f"Removed participant {identity} from room {room_name}")
            return True
        else:
            logger.warning(f"Participant {identity} not found in room {room_name}")
            return False
            
    except Exception as e:
        logger.error(f"Error removing participant: {str(e)}")
        return False

# Pydantic models for request/response
class TokenRequest(BaseModel):
    room_name: str
    identity: str

class TokenResponse(BaseModel):
    accessToken: str

class RoomInfo(BaseModel):
    name: str
    sid: str
    num_participants: int
    creation_time: int

class RoomsResponse(BaseModel):
    rooms: list[RoomInfo]

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
    Generate a LiveKit access token for a client and ensure the room exists.
    
    Args:
        room_name: The name of the room to join
        identity: The identity/name of the participant
    
    Returns:
        TokenResponse containing the access token
    """
    try:
        # Ensure room exists
        await create_room_if_not_exists(room_name)
        
        # Create access token using LiveKit SDK
        access_token = create_livekit_token(room_name, identity)
        
        logger.info(f"Generated LiveKit token for {identity} in room {room_name}")
        
        return TokenResponse(accessToken=access_token)
    
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate access token")

@app.get("/rooms")
async def get_rooms() -> RoomsResponse:
    """
    List all active LiveKit rooms.
    
    Returns:
        RoomsResponse containing list of active rooms
    """
    try:
        rooms = await list_rooms()
        
        room_list = []
        for room in rooms:
            room_list.append(RoomInfo(
                name=room.name,
                sid=room.sid,
                num_participants=room.num_participants,
                creation_time=room.creation_time
            ))
        
        logger.info(f"Listed {len(room_list)} active rooms")
        return RoomsResponse(rooms=room_list)
    
    except Exception as e:
        logger.error(f"Error listing rooms: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list rooms")

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
        # Initialize Groq client if not already done
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            # Return a mock summary for testing purposes
            summary = f"Mock Summary: Call context provided - {request.call_context[:100]}... (Please configure GROQ_API_KEY for AI-generated summaries)"
            logger.info("Generated mock summary for transfer (GROQ_API_KEY not configured)")
            return TransferResponse(summary=summary)
        
        # Call Groq API to generate summary
        global groq_client
        if groq_client is None:
            groq_client = Groq(api_key=GROQ_API_KEY)
            
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
    Complete the transfer by removing Agent A from the original room.
    
    Args:
        request: CompleteTransferRequest with room and agent details
    
    Returns:
        SuccessResponse confirming the transfer completion
    """
    try:
        # Remove Agent A from the original room using LiveKit API
        success = await remove_participant_from_room(
            request.original_room_name, 
            request.agent_a_identity
        )
        
        if success:
            logger.info(f"Successfully removed {request.agent_a_identity} from room {request.original_room_name}")
            return SuccessResponse(
                success=True, 
                message=f"Transfer completed. {request.agent_a_identity} removed from {request.original_room_name}"
            )
        else:
            logger.warning(f"Could not remove {request.agent_a_identity} from room {request.original_room_name}")
            return SuccessResponse(
                success=False,
                message=f"Transfer signal sent, but could not automatically remove participant. Manual disconnect may be required."
            )
    
    except Exception as e:
        logger.error(f"Error completing transfer: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete transfer")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)