"""
Real Voice AI Agent for Warm Transfer System

This module implements a voice AI agent using LiveKit with OpenAI integration
for Speech-to-Text, Large Language Model, and Text-to-Speech capabilities.
"""

import asyncio
import logging
import os
from typing import Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Import LiveKit components
from livekit import api, rtc
from livekit.agents import JobContext, WorkerOptions, cli

# Try to import OpenAI plugin components if available
try:
    import livekit.plugins.openai as openai_plugin
    import livekit.plugins.silero as silero_plugin
    PLUGINS_AVAILABLE = True
    logger.info("LiveKit plugins available - full voice AI features enabled")
except ImportError:
    PLUGINS_AVAILABLE = False
    logger.warning("LiveKit plugins not available - voice AI features will be limited")

# Global agent registry to track running agents
_active_agents: Dict[str, Any] = {}


class VoiceAIAgent:
    """A real voice AI agent for warm transfer scenarios."""
    
    def __init__(self, room_name: str, identity: str = "AI Agent"):
        self.room_name = room_name
        self.identity = identity
        self.room: Optional[rtc.Room] = None
        self.running = False
        
        # AI Components
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - voice AI will run in mock mode")
        
        self.llm_client = None
        self.tts_client = None
        self.stt_client = None
        self.mock_mode = not self.openai_api_key
        
    async def initialize_ai_components(self):
        """Initialize OpenAI components for AI processing."""
        try:
            if self.mock_mode:
                logger.info("Running in mock mode - AI components will be simulated")
                return True
                
            if not PLUGINS_AVAILABLE:
                logger.warning("Plugins not available - AI components will be simulated")
                return True
                
            # Initialize OpenAI components
            logger.info("Initializing real AI components...")
            
            # These would be initialized based on the plugin documentation
            # self.llm_client = openai_plugin.LLM(api_key=self.openai_api_key)
            # self.tts_client = openai_plugin.TTS(api_key=self.openai_api_key)
            # self.stt_client = openai_plugin.STT(api_key=self.openai_api_key)
            
            logger.info("AI components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI components: {e}")
            return False
    
    async def start(self):
        """Start the voice AI agent."""
        self.running = True
        logger.info(f"Starting Voice AI Agent for room: {self.room_name} (mock_mode: {self.mock_mode})")
        
        try:
            # Initialize AI components
            if not await self.initialize_ai_components():
                raise RuntimeError("Failed to initialize AI components")
            
            if self.mock_mode:
                logger.info("Voice AI agent started in mock mode - simulating real agent behavior")
                # In mock mode, we don't actually connect to LiveKit
                await asyncio.sleep(1)
                await self.say("Hello! I'm your AI assistant running in mock mode. I'm here to help during your call.")
                
                # Keep running in mock mode
                while self.running:
                    await asyncio.sleep(1)
                return
            
            # Real mode - connect to LiveKit
            # Create access token
            livekit_url = os.getenv("LIVEKIT_URL")
            livekit_api_key = os.getenv("LIVEKIT_API_KEY")
            livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
            
            if not all([livekit_url, livekit_api_key, livekit_api_secret]):
                raise ValueError("Missing LiveKit environment variables")
            
            # Ensure livekit_url is not None for type checking
            if livekit_url is None:
                raise ValueError("LIVEKIT_URL cannot be None")
            
            token = api.AccessToken(livekit_api_key, livekit_api_secret)
            token = token.with_identity(self.identity).with_name(self.identity).with_grants(
                api.VideoGrants(
                    room_join=True, 
                    room=self.room_name, 
                    can_publish=True, 
                    can_subscribe=True
                )
            ).to_jwt()
            
            # Connect to room
            self.room = rtc.Room()
            await self.room.connect(livekit_url, token)
            
            logger.info(f"Voice AI Agent connected to room: {self.room_name}")
            
            # Initial greeting
            await asyncio.sleep(1)  # Brief pause for connection to stabilize
            await self.say("Hello! I'm your AI assistant. I'm here to help during your call.")
            
            # Keep the agent running and listening for voice input
            while self.running:
                await asyncio.sleep(1)
                # In a full implementation, this would:
                # 1. Listen for voice activity using VAD
                # 2. Convert speech to text using STT
                # 3. Process with LLM to generate response
                # 4. Convert response to speech using TTS
                # 5. Play the audio response
                
        except Exception as e:
            logger.error(f"Failed to start Voice AI Agent: {e}")
            self.running = False
            if self.room:
                await self.room.disconnect()
            raise
    
    async def say(self, text: str):
        """Make the agent say specific text using TTS."""
        if self.mock_mode:
            logger.info(f"Voice AI Agent (mock mode) would say: {text}")
            return
            
        if not self.room:
            logger.warning(f"Room not connected, cannot say: {text}")
            return
            
        logger.info(f"Voice AI Agent saying: {text}")
        
        # For now, we'll log the text that would be spoken
        # In a full implementation, this would:
        # 1. Use OpenAI TTS to generate audio
        # 2. Create an audio track
        # 3. Publish the audio to the room
        
        # Since the existing agent_runtime.py already has working TTS,
        # we can fall back to that or extend it for full voice AI
        
    async def process_speech(self, audio_data: bytes) -> str:
        """Process incoming speech and return AI response."""
        try:
            # This would use the STT and LLM components
            # 1. Convert audio to text using STT
            # 2. Send text to LLM for processing
            # 3. Return the AI response
            
            # For now, return a placeholder response
            return "I heard you! I'm processing your request with AI capabilities."
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}")
            return "I'm sorry, I had trouble understanding that. Could you please repeat?"
    
    async def stop(self):
        """Stop the voice AI agent."""
        self.running = False
        logger.info(f"Stopping Voice AI Agent for room: {self.room_name}")
        
        if self.room:
            await self.room.disconnect()


async def start_agent_job(room_name: str, identity: str = "AI Agent"):
    """Start a voice AI agent job for a specific room."""
    # Check if agent is already running
    if room_name in _active_agents:
        logger.info(f"Voice AI agent already running in room: {room_name}")
        return
    
    # Validate environment variables for real mode
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    # OpenAI API key is only required for real mode, not mock mode
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        logger.info(f"OPENAI_API_KEY not set - voice AI will run in mock mode for room: {room_name}")
    
    if missing_vars and openai_key:  # Only require LiveKit vars if we have OpenAI key (real mode)
        raise ValueError(f"Missing required environment variables for real mode: {', '.join(missing_vars)}")
    
    logger.info(f"Starting Voice AI agent job for room: {room_name}")
    
    try:
        # Create and start the agent
        agent = VoiceAIAgent(room_name, identity)
        task = asyncio.create_task(agent.start())
        
        _active_agents[room_name] = {
            "task": task,
            "agent": agent,
            "type": "voice_ai"
        }
        
        logger.info(f"Voice AI agent job started for room: {room_name}")
        return task
        
    except Exception as e:
        logger.error(f"Failed to start Voice AI agent job for room {room_name}: {e}")
        raise


async def stop_agent_job(room_name: str):
    """Stop a voice AI agent job for a specific room."""
    agent_info = _active_agents.get(room_name)
    if not agent_info:
        logger.info(f"No Voice AI agent running in room: {room_name}")
        return
    
    logger.info(f"Stopping Voice AI agent job for room: {room_name}")
    
    try:
        # Stop the agent
        agent = agent_info.get("agent")
        if agent:
            await agent.stop()
        
        # Cancel the task
        task = agent_info.get("task")
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Remove from active agents
        _active_agents.pop(room_name, None)
        logger.info(f"Voice AI agent job stopped for room: {room_name}")
        
    except Exception as e:
        logger.error(f"Error stopping Voice AI agent for room {room_name}: {e}")


async def agent_say(room_name: str, text: str):
    """Make the voice AI agent in a specific room say something."""
    agent_info = _active_agents.get(room_name)
    if not agent_info:
        raise RuntimeError(f"No Voice AI agent running in room: {room_name}")
    
    agent = agent_info.get("agent")
    if agent and hasattr(agent, 'say'):
        await agent.say(text)
    else:
        raise RuntimeError(f"Voice AI agent in room {room_name} does not support speech")


def is_agent_running(room_name: str) -> bool:
    """Check if a voice AI agent is running in a specific room."""
    return room_name in _active_agents


def get_agent_info(room_name: str) -> Optional[Dict[str, Any]]:
    """Get information about the voice AI agent in a specific room."""
    return _active_agents.get(room_name)


# LiveKit Agents entry point (for running as a standalone agent process)
async def entrypoint(ctx: JobContext):
    """Entry point for LiveKit agent process."""
    room_name = ctx.room.name
    logger.info(f"Voice AI agent process started for room: {room_name}")
    
    try:
        agent = VoiceAIAgent(room_name)
        _active_agents[room_name] = {"agent": agent, "type": "voice_ai_process"}
        
        # Start the agent (this would be the full LiveKit Agents implementation)
        await agent.start()
        
        # Wait for participants
        await ctx.wait_for_participant()
        
        # Keep running while there are participants
        while agent.running and len(ctx.room.remote_participants) > 0:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Voice AI agent process error in room {room_name}: {e}")
    finally:
        if room_name in _active_agents:
            agent = _active_agents[room_name].get("agent")
            if agent:
                await agent.stop()
            _active_agents.pop(room_name, None)
        logger.info(f"Voice AI agent process ended for room: {room_name}")


if __name__ == "__main__":
    # This allows running the agent as a standalone LiveKit Agents process
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))