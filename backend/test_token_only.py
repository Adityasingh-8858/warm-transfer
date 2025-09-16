#!/usr/bin/env python3
"""
Test the LiveKit token generation function directly
"""

import os
from dotenv import load_dotenv
from livekit import api

# Load environment variables
load_dotenv()

def test_livekit_token_generation():
    """Test LiveKit token generation directly"""
    
    # Get environment variables
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
    
    print("🧪 Testing LiveKit Token Generation")
    print("=" * 50)
    
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        print("❌ Missing LiveKit API credentials in environment variables")
        return False
    
    print(f"✅ API Key: {LIVEKIT_API_KEY[:10]}...")
    print(f"✅ API Secret: {LIVEKIT_API_SECRET[:10]}...")
    
    try:
        # Test token generation
        print("\n🔑 Generating Access Token...")
        
        room_name = "test-room"
        identity = "test-user"
        
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(identity) \
            .with_name(identity) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )).to_jwt()
        
        print(f"✅ Token generated successfully!")
        print(f"🏠 Room: {room_name}")
        print(f"👤 Identity: {identity}")
        print(f"🎫 Token length: {len(token)} characters")
        print(f"🔑 Token (first 50 chars): {token[:50]}...")
        
        # Test with different parameters
        print("\n🔄 Testing with different parameters...")
        
        token2 = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity("agent-a") \
            .with_name("Agent A") \
            .with_grants(api.VideoGrants(
                room_join=True,
                room="support-room-123",
                can_publish=True,
                can_subscribe=True,
            )).to_jwt()
        
        print(f"✅ Second token generated successfully!")
        print(f"🎫 Token length: {len(token2)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating token: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_livekit_token_generation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 LiveKit token generation is working properly!")
        print("The backend should be able to generate tokens for live audio calls.")
    else:
        print("⚠️  Token generation failed. Check your LiveKit credentials.")
    
    exit(0 if success else 1)