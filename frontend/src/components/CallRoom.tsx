'use client';

import { useState, useRef } from 'react';
import { LiveKitRoom, VideoConference, ControlBar } from '@livekit/components-react';
import '@livekit/components-styles';

interface CallRoomProps {
  token: string;
  roomName: string;
  identity: string;
  onLeave: () => void;
}

export default function CallRoom({ token, roomName, identity, onLeave }: CallRoomProps) {
  const [isTransferring, setIsTransferring] = useState(false);
  const [transferSummary, setTransferSummary] = useState('');
  const [showSummary, setShowSummary] = useState(false);
  const [callContext, setCallContext] = useState('');
  const [showContextInput, setShowContextInput] = useState(false);

  const isAgentA = identity.toLowerCase().includes('agent a') || identity.toLowerCase() === 'agent a';

  const handleWarmTransfer = async () => {
    if (!callContext.trim()) {
      setShowContextInput(true);
      return;
    }

    setIsTransferring(true);
    try {
      const response = await fetch('http://localhost:8000/initiate-transfer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          call_context: callContext
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to initiate transfer');
      }

      const data = await response.json();
      setTransferSummary(data.summary);
      setShowSummary(true);
    } catch (error) {
      console.error('Error initiating transfer:', error);
      alert('Failed to initiate transfer. Please try again.');
    } finally {
      setIsTransferring(false);
    }
  };

  const handleCompleteTransfer = async () => {
    try {
      const response = await fetch('http://localhost:8000/complete-transfer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          original_room_name: roomName,
          agent_a_identity: identity,
          agent_b_identity: 'Agent B' // This would normally come from the UI
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to complete transfer');
      }

      alert('Transfer completed successfully. You have been removed from the call.');
      onLeave();
    } catch (error) {
      console.error('Error completing transfer:', error);
      alert('Failed to complete transfer. Please try again.');
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-4 py-3 flex justify-between items-center">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">
            Room: {roomName}
          </h1>
          <p className="text-sm text-gray-600">
            Connected as: {identity}
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          {isAgentA && (
            <>
              {!showSummary && (
                <button
                  onClick={() => setShowContextInput(!showContextInput)}
                  className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition duration-200"
                >
                  Warm Transfer
                </button>
              )}
              {showSummary && (
                <button
                  onClick={handleCompleteTransfer}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition duration-200"
                >
                  Complete Transfer
                </button>
              )}
            </>
          )}
          
          <button
            onClick={onLeave}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition duration-200"
          >
            Leave Room
          </button>
        </div>
      </div>

      {/* Context Input Modal */}
      {showContextInput && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Call Context for Transfer</h3>
            <textarea
              value={callContext}
              onChange={(e) => setCallContext(e.target.value)}
              placeholder="Describe the current call situation, customer issue, and any important details for the next agent..."
              className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
            />
            <div className="flex justify-end space-x-3 mt-4">
              <button
                onClick={() => setShowContextInput(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={handleWarmTransfer}
                disabled={isTransferring || !callContext.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isTransferring ? 'Generating Summary...' : 'Generate Summary'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Transfer Summary Modal */}
      {showSummary && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <h3 className="text-lg font-semibold mb-4">Call Summary for Agent B</h3>
            <div className="bg-gray-50 p-4 rounded-lg mb-4">
              <p className="text-gray-800 whitespace-pre-wrap">{transferSummary}</p>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Share this summary with Agent B before completing the transfer.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowSummary(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Edit Context
              </button>
              <button
                onClick={handleCompleteTransfer}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
              >
                Complete Transfer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Video Conference Area */}
      <div className="flex-1">
        <LiveKitRoom
          video={true}
          audio={true}
          token={token}
          serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL || 'ws://localhost:7880'}
          data-lk-theme="default"
          style={{ height: '100%' }}
        >
          <VideoConference />
        </LiveKitRoom>
      </div>
    </div>
  );
}