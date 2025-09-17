"""
Test script for Voice AI Agent functionality
"""

import asyncio
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_voice_ai_setup():
    """Test if voice AI agent dependencies are properly installed."""
    logger.info("Testing Voice AI Agent setup...")
    
    # Test 1: Check environment variables
    logger.info("Checking environment variables...")
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    optional_vars = ["OPENAI_API_KEY"]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            logger.info(f"✓ {var}: Set")
    
    for var in optional_vars:
        if not os.getenv(var):
            logger.warning(f"⚠ {var}: Not set (required for Voice AI)")
        else:
            logger.info(f"✓ {var}: Set")
    
    if missing_required:
        logger.error(f"❌ Missing required variables: {', '.join(missing_required)}")
        return False
    
    # Test 2: Import dependencies
    logger.info("Testing imports...")
    try:
        from livekit.agents import JobContext, WorkerOptions, cli, llm
        logger.info("✓ livekit.agents imported")
        
        from livekit.agents.voice_assistant import VoiceAssistant
        logger.info("✓ VoiceAssistant imported")
        
        from livekit.plugins import openai, silero
        logger.info("✓ OpenAI and Silero plugins imported")
        
        from livekit import api, rtc
        logger.info("✓ LiveKit API and RTC imported")
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    
    # Test 3: Test voice_agent module
    logger.info("Testing voice_agent module...")
    try:
        import voice_agent
        logger.info("✓ voice_agent module imported")
        
        if hasattr(voice_agent, 'start_agent_job'):
            logger.info("✓ start_agent_job function available")
        else:
            logger.warning("⚠ start_agent_job function not found")
        
    except ImportError as e:
        logger.error(f"❌ voice_agent import error: {e}")
        return False
    
    # Test 4: Test agent_runtime integration
    logger.info("Testing agent_runtime integration...")
    try:
        import agent_runtime
        logger.info("✓ agent_runtime imported")
        
        # Check if VOICE_AI_AVAILABLE is properly detected
        if hasattr(agent_runtime, 'VOICE_AI_AVAILABLE'):
            if agent_runtime.VOICE_AI_AVAILABLE:
                logger.info("✓ Voice AI detected as available")
            else:
                logger.warning("⚠ Voice AI not detected as available")
        
    except ImportError as e:
        logger.error(f"❌ agent_runtime import error: {e}")
        return False
    
    logger.info("🎉 Voice AI Agent setup test completed!")
    
    # Test 5: Agent Manager functionality
    logger.info("Testing AgentManager...")
    try:
        manager = agent_runtime.manager
        logger.info("✓ AgentManager instance created")
        
        # Test configuration status
        enable_voice_ai = os.getenv("ENABLE_VOICE_AI", "0") == "1"
        enable_mock = os.getenv("ENABLE_AGENT_MOCK", "1") == "1"
        
        logger.info(f"Configuration: ENABLE_VOICE_AI={enable_voice_ai}, ENABLE_AGENT_MOCK={enable_mock}")
        
        if enable_voice_ai and not enable_mock:
            logger.info("✓ Voice AI mode will be enabled")
        elif not enable_mock:
            logger.info("✓ Basic real agent mode will be enabled")
        else:
            logger.info("✓ Mock agent mode will be enabled")
            
    except Exception as e:
        logger.error(f"❌ AgentManager test error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_voice_ai_setup())
    if success:
        print("\n✅ Voice AI Agent setup is ready!")
        print("\nTo enable Voice AI:")
        print("1. Set OPENAI_API_KEY in your .env file")
        print("2. Set ENABLE_VOICE_AI=1 in your .env file") 
        print("3. Set ENABLE_AGENT_MOCK=0 in your .env file")
        print("4. Restart the backend server")
    else:
        print("\n❌ Voice AI Agent setup has issues. Check the logs above.")