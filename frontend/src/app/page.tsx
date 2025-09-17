"use client";

import { useState, useEffect, useCallback } from 'react';
import {
  LiveKitRoom,
  VideoConference,
} from "@livekit/components-react";
import '@livekit/components-styles';

interface TransferSummaryState {
  loading: boolean;
  text: string | null;
  error: string | null;
}

interface RecentTransfer {
  id: string;
  summary?: string;
  room_name?: string;
  agent_a?: string;
  created_at?: number;
}

export default function Home() {
  const [joined, setJoined] = useState(false);
  const [roomName, setRoomName] = useState('');
  const [identity, setIdentity] = useState('');
  const [token, setToken] = useState('');
  const [summary, setSummary] = useState<TransferSummaryState>({ loading: false, text: null, error: null });
  const [agentA, setAgentA] = useState('');
  const [agentB, setAgentB] = useState('');
  const [participants, setParticipants] = useState<string[]>([]);
  const [transferId, setTransferId] = useState<string | null>(null);
  const [briefingRoom, setBriefingRoom] = useState<string | null>(null);
  const [isOnHold, setIsOnHold] = useState<boolean>(false);
  const [recentTransfers, setRecentTransfers] = useState<RecentTransfer[]>([]);

  // Poll participants list (simple demo polling)
  useEffect(() => {
    if (!joined || !roomName) return;
    let active = true;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/participants?room_name=${encodeURIComponent(roomName)}`);
        if (!res.ok) return;
        const data = await res.json();
  type P = { identity: string };
  if (active) setParticipants((data.participants as P[] | undefined)?.map((p) => p.identity) || []);
      } catch { /* ignore */ }
    }, 4000);
    return () => { active = false; clearInterval(interval); };
  }, [joined, roomName]);

  const initiateTransfer = useCallback(async () => {
    setSummary({ loading: true, text: null, error: null });
    try {
      const context = `Conversation so far in room ${roomName} with participants: ${participants.join(', ') || 'none yet'}. Initiated by ${identity}.`;
      const res = await fetch('http://localhost:8000/initiate-transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ call_context: context, room_name: roomName, agent_a_identity: identity })
      });
      if (!res.ok) throw new Error('Failed to generate summary');
      const data = await res.json();
      setSummary({ loading: false, text: data.summary, error: null });
      setAgentA(identity); // assume current user is agent A initiating
      setTransferId(data.id || null);
      setBriefingRoom(data.briefing_room_name || null);
      // Set on-hold state when briefing room is created
      if (data.briefing_room_name) {
        setIsOnHold(true);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error';
      setSummary({ loading: false, text: null, error: message });
    }
  }, [roomName, participants, identity]);

  const completeTransfer = useCallback(async () => {
    if (!agentA || !agentB) {
      alert('Need Agent A (auto-set) and Agent B (enter below)');
      return;
    }
    try {
      const res = await fetch('http://localhost:8000/complete-transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ original_room_name: roomName, agent_a_identity: agentA, agent_b_identity: agentB, transfer_id: transferId })
      });
      const data = await res.json();
      alert(data.message);
      // Clear on-hold state after transfer completion
      setIsOnHold(false);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'unknown';
      alert('Error completing transfer: ' + message);
    }
  }, [agentA, agentB, roomName, transferId]);

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
    setSummary({ loading: false, text: null, error: null });
    setParticipants([]);
    setAgentA('');
    setAgentB('');
    setTransferId(null);
    setBriefingRoom(null);
    setIsOnHold(false);
  };

  // Poll recent transfers (independent of room join)
  useEffect(() => {
    let active = true;
    const fetchTransfers = async () => {
      try {
        const resp = await fetch('http://localhost:8000/transfers?limit=10');
        if (!resp.ok) return;
        const data = await resp.json();
        if (active) setRecentTransfers(data.transfers || []);
      } catch {/* ignore */}
    };
    fetchTransfers();
    const intv = setInterval(fetchTransfers, 8000);
    return () => { active = false; clearInterval(intv); };
  }, []);

  if (joined) {
    return (
      <div className="min-h-screen flex flex-col items-start md:items-center p-4 gap-4">
        <div className="w-full flex flex-col md:flex-row gap-4 max-w-6xl">
          <div className="bg-white rounded-lg shadow p-4 w-full md:w-2/3">
            <h2 className="text-xl font-semibold mb-2">Room: {roomName}</h2>
            <p className="text-sm text-black mb-3">Connected as {identity}</p>
            <div className="h-[480px] border rounded overflow-hidden relative">
              {isOnHold && (
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
                  <div className="bg-white rounded-lg p-6 text-center shadow-xl">
                    <div className="text-2xl mb-2">⏸️</div>
                    <div className="font-semibold text-gray-800 mb-1">Call On Hold</div>
                    <div className="text-sm text-gray-600">Agent A is briefing Agent B</div>
                    <div className="mt-3 text-xs text-gray-500">
                      Transfer will complete automatically when Agent A exits
                    </div>
                  </div>
                </div>
              )}
              <LiveKitRoom
                token={token}
                serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL || 'wss://INVALID_IF_NOT_SET'}
                connectOptions={{ autoSubscribe: true }}
                audio={true}
                video={true}
                onDisconnected={handleLeaveRoom}
              >
                <VideoConference />
              </LiveKitRoom>
            </div>
            <div className="mt-4 flex gap-2 flex-wrap text-xs text-black">
              <span className="font-medium">Participants:</span>
              {participants.length ? participants.map((p: string) => <span key={p} className="px-2 py-0.5 bg-gray-100 rounded">{p}</span>) : <span>none</span>}
            </div>
            <button onClick={handleLeaveRoom} className="mt-4 bg-red-600 text-black px-3 py-2 rounded hover:bg-red-700 text-sm">Leave Room</button>
          </div>
          <div className="bg-white rounded-lg shadow p-4 w-full md:w-1/3 space-y-4">
            <h3 className="font-semibold">Warm Transfer</h3>
            <div className="space-y-2">
              <button disabled={summary.loading} onClick={initiateTransfer} className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50">
                {summary.loading ? 'Generating summary...' : 'Generate Transfer Summary'}
              </button>
              {summary.error && <p className="text-xs text-red-600">{summary.error}</p>}
              {summary.text && (
                <div className="text-xs bg-gray-50 border p-2 rounded max-h-48 overflow-auto whitespace-pre-wrap">
                  {summary.text}
                </div>
              )}
              {transferId && (
                <p className="text-[10px] text-gray-400">Transfer ID: {transferId}</p>
              )}
            </div>
            <div className="border-t pt-3 space-y-2">
              {briefingRoom && (
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded text-xs text-black">
                  <div className="font-medium mb-2 text-yellow-800">📞 Briefing Room Created</div>
                  <div className="font-mono break-all mb-2 p-1 bg-white rounded border">{briefingRoom}</div>
                  
                  <div className="mb-3 p-2 bg-blue-50 border-l-4 border-blue-400">
                    <div className="font-medium text-blue-800 mb-1">Agent B Instructions:</div>
                    <div className="text-blue-700 text-[11px] leading-tight">
                      1. Open new tab → http://localhost:3000<br/>
                      2. Enter identity: &ldquo;Agent B&rdquo;<br/>
                      3. Room name: <span className="font-mono bg-white px-1 rounded">{briefingRoom}</span><br/>
                      4. Click &ldquo;Join Room&rdquo; to receive briefing
                    </div>
                  </div>

                  <div className="flex gap-2 flex-wrap">
                    <button
                      className="bg-yellow-600 text-white px-2 py-1 rounded text-[11px]"
                      onClick={() => navigator.clipboard.writeText(briefingRoom!)}
                    >📋 Copy Room Name</button>
                    <button
                      className="bg-blue-600 text-white px-2 py-1 rounded text-[11px]"
                      onClick={() => {
                        const url = `http://localhost:3000?room=${encodeURIComponent(briefingRoom!)}&identity=Agent%20B`;
                        navigator.clipboard.writeText(url);
                        alert('Agent B join link copied to clipboard!');
                      }}
                    >🔗 Copy Agent B Link</button>
                    <button
                      className="bg-gray-700 text-white px-2 py-1 rounded text-[11px]"
                      onClick={async () => {
                        try {
                          const resp = await fetch(`http://localhost:8000/get-token?room_name=${encodeURIComponent(briefingRoom!)}&identity=${encodeURIComponent(identity + '-A')}`);
                          if (!resp.ok) throw new Error('Failed to get token');
                          const data = await resp.json();
                          // naive join in same tab by swapping token/room
                          setToken(data.accessToken);
                          setRoomName(briefingRoom!);
                        } catch (e: unknown) {
                          const msg = e instanceof Error ? `: ${e.message}` : '';
                          alert('Could not join briefing room' + msg);
                        }
                      }}
                    >🎯 Join as Agent A</button>
                  </div>
                </div>
              )}
              <label className="block text-xs font-medium text-gray-700">Agent B Identity</label>
              <input value={agentB} onChange={e=>setAgentB(e.target.value)} className="w-full border px-2 py-1 rounded text-sm" placeholder="Agent B" />
              <button onClick={completeTransfer} className="w-full bg-emerald-600 text-white py-2 rounded text-sm hover:bg-emerald-700">Complete Transfer</button>
            </div>
            <div className="border-t pt-3 space-y-1">
              <h4 className="text-xs font-semibold text-gray-700">Recent Transfers</h4>
              <div className="max-h-40 overflow-auto space-y-1">
                {recentTransfers.length ? recentTransfers.map((t: RecentTransfer) => (
                  <div key={t.id} className="text-[10px] p-1 border rounded bg-gray-50">
                    <div className="font-mono truncate">{t.id}</div>
                    <div className="truncate">{t.summary?.slice(0,60)}{t.summary && t.summary.length>60?'...':''}</div>
                  </div>
                )) : <p className="text-[10px] text-gray-400">No transfers yet</p>}
              </div>
            </div>
            <div className="text-[10px] text-gray-400 break-all">
              <strong>Token:</strong> {token.slice(0,32)}...
            </div>
          </div>
        </div>
      </div>
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
