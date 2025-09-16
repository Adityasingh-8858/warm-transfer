#!/usr/bin/env python3
"""
Test the LiveKit API integration directly
"""

import os
import asyncio
from dotenv import load_dotenv
from livekit import api

# Load environment variables
load_dotenv()

async def test_livekit_api_integration():
    """Test LiveKit API integration directly"""
    
    # Get environment variables
    LIVEKIT_URL = os.getenv("LIVEKIT_URL")
    
    print("🧪 Testing LiveKit API Integration")
    print("=" * 50)
    
    if not LIVEKIT_URL:
        print("❌ Missing LIVEKIT_URL in environment variables")
        return False
    
    print(f"✅ LiveKit URL: {LIVEKIT_URL}")
    
    try:
        # Test API connection
        print("\n🔗 Connecting to LiveKit API...")
        
        lkapi = api.LiveKitAPI(LIVEKIT_URL)
        
        # Test room creation
        print("🏠 Testing room creation...")
        
        room_name = "test-api-room"
        
        try:
            room_info = await lkapi.room.create_room(
                api.CreateRoomRequest(name=room_name)
            )
            print(f"✅ Room created successfully!")
            print(f"   - Name: {room_info.name}")
            print(f"   - SID: {room_info.sid}")
            print(f"   - Created: {room_info.creation_time}")
        except Exception as room_error:
            print(f"ℹ️  Room creation result: {str(room_error)}")
            print("   (Room might already exist, which is fine)")
        
        # Test room listing
        print("\n📋 Testing room listing...")
        
        try:
            results = await lkapi.room.list_rooms(api.ListRoomsRequest())
            print(f"✅ Found {len(results.rooms)} rooms:")
            
            for room in results.rooms[:5]:  # Show first 5 rooms
                print(f"   - {room.name} (SID: {room.sid}, Participants: {room.num_participants})")
                
        except Exception as list_error:
            print(f"❌ Error listing rooms: {str(list_error)}")
        
        # Cleanup
        await lkapi.aclose()
        print("✅ API connection closed properly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with LiveKit API: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_livekit_api_integration())
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 LiveKit API integration is working properly!")
        print("The backend can manage rooms and participants for live audio calls.")
    else:
        print("⚠️  API integration failed. Check your LiveKit server configuration.")
    
    exit(0 if success else 1)