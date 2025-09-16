'use client';

import { useState } from 'react';

interface CallRoomProps {
  token: string;
  roomName: string;
  identity: string;
  onLeave: () => void;
}

const CallRoom: React.FC<CallRoomProps> = ({ token, roomName, identity, onLeave }) => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-2xl">
        <h2 className="text-2xl font-bold mb-4">Room: {roomName}</h2>
        <p className="text-gray-600 mb-4">Connected as {identity}</p>
        <div className="text-xs bg-gray-100 p-2 rounded mb-4 overflow-auto">
          <strong>Token (truncated):</strong> {token ? token.slice(0, 16) + '...' : 'N/A'}
        </div>
        <button
          onClick={onLeave}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 transition"
        >
          Leave Room
        </button>
      </div>
    </div>
  );
};

export default function Home() {
  const [joined, setJoined] = useState(false);
  const [roomName, setRoomName] = useState('');
  const [identity, setIdentity] = useState('');
  const [token, setToken] = useState('');

  const handleJoinRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!roomName.trim() || !identity.trim()) {
      alert('Please enter both room name and your name');
      return;
    }

    try {
      // Get token from backend
      const response = await fetch(
        `http://localhost:8000/get-token?room_name=${encodeURIComponent(roomName)}&identity=${encodeURIComponent(identity)}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to get access token');
      }
      
      const data = await response.json();
      setToken(data.accessToken);
      setJoined(true);
    } catch (error) {
      console.error('Error joining room:', error);
      alert('Failed to join room. Please check your connection and try again.');
    }
  };

  const handleLeaveRoom = () => {
    setJoined(false);
    setToken('');
  };

  if (joined) {
    return (
      <CallRoom
        token={token}
        roomName={roomName}
        identity={identity}
        onLeave={handleLeaveRoom}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Warm Transfer System
          </h1>
          <p className="text-gray-600">
            Enter your details to join a call room
          </p>
        </div>

        <form onSubmit={handleJoinRoom} className="space-y-6">
          <div>
            <label htmlFor="identity" className="block text-sm font-medium text-gray-700 mb-2">
              Your Name
            </label>
            <input
              type="text"
              id="identity"
              value={identity}
              onChange={(e) => setIdentity(e.target.value)}
              placeholder="Enter your name (e.g., Agent A, Agent B, Customer)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label htmlFor="roomName" className="block text-sm font-medium text-gray-700 mb-2">
              Room Name
            </label>
            <input
              type="text"
              id="roomName"
              value={roomName}
              onChange={(e) => setRoomName(e.target.value)}
              placeholder="Enter room name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200"
          >
            Join Room
          </button>
        </form>

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Quick Start Guide:</h3>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>• Customer joins first with room name</li>
            <li>• Agent A joins same room</li>
            <li>• Agent A initiates warm transfer to Agent B</li>
            <li>• Agent B joins after receiving briefing</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
