# Warm Transfer Application

A real-time communication system that facilitates warm call transfers between agents using LiveKit and AI-powered call summaries.

## 🎯 Overview

This application enables seamless warm transfers where Agent A can brief Agent B about a customer call before transferring the conversation. The system uses LiveKit for real-time video/audio communication and Groq LLM for generating intelligent call summaries.

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI** framework for REST API endpoints
- **LiveKit Python SDK** for official token generation and room management
- **LiveKit API** for creating/managing rooms and participants
- **Groq API** integration for AI-powered call summaries
- **Environment-based configuration** for security
- **Proper participant removal** for clean transfers

### Frontend (Next.js/React)
- **Next.js 15** with TypeScript and Tailwind CSS
- **LiveKit React Components** for video conferencing UI
- **React hooks** for state management
- **Responsive design** for optimal user experience

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- Node.js 18+
- LiveKit account and server
- Groq API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd warm-call
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit `backend/.env` with your credentials:
```env
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here
LIVEKIT_URL=wss://your-livekit-server.com
GROQ_API_KEY=your_groq_api_key_here
HOST=127.0.0.1
PORT=8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
```

Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-server.com
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 4. Start Development Servers

**Option A: Use provided scripts**
```bash
# Windows
start-dev.bat

# macOS/Linux
chmod +x start-dev.sh
./start-dev.sh
```

**Option B: Manual startup**

Terminal 1 (Backend):
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 API Endpoints

### GET `/get-token`
Generate LiveKit access token for room participation using official LiveKit Python SDK.

**Query Parameters:**
- `room_name` (string): Target room name
- `identity` (string): Participant identity/name

**Response:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Features:**
- ✅ Official LiveKit SDK token generation
- ✅ Automatic room creation if it doesn't exist
- ✅ Proper video/audio permissions granted
- ✅ Secure JWT signing with API credentials

### GET `/rooms`
### GET `/participants`
List participants currently in a specific LiveKit room.

Query Parameters:
- `room_name` (string): Target room name

Response:
```json
{
  "room": "support-room-1",
  "participants": [
    { "identity": "Agent A", "name": "Agent A", "metadata": null }
  ]
}
```

Notes:
- Returns an empty list (instead of 500) if listing fails to keep UI resilient.

List all active LiveKit rooms and their participants.

**Response:**
```json
{
  "rooms": [
    {
      "name": "customer-support-room-1",
      "sid": "RM_abc123",
      "num_participants": 2,
      "creation_time": 1699123456
    }
  ]
}
```

### POST `/initiate-transfer`
Generate AI summary of call context for warm transfer.

**Request Body:**
```json
{
  "call_context": "Customer John Smith called about billing issue with account #12345..."
}
```

**Response:**
```json
{
  "summary": "Customer John Smith is experiencing billing discrepancies...",
  "id": "b1a0d5b0-0e5d-4a9c-8e76-5fd4d0c6b9e2"
}
```

Notes:
- If `GROQ_API_KEY` is missing or `FORCE_MOCK_GROQ=1`, returns a mock summary for local development.
- Summary is persisted (SQLite) and the record ID is returned.


### POST `/complete-transfer`
Finalize transfer by removing Agent A from the original room using LiveKit API.

**Request Body:**
```json
{
  "original_room_name": "customer-support-room-1",
  "agent_a_identity": "Agent A",
  "agent_b_identity": "Agent B"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Transfer completed. Agent A removed from customer-support-room-1"
}
```

**Features:**
- ✅ Automatic participant removal via LiveKit API
- ✅ Proper error handling for disconnection issues
- ✅ Clean transfer completion without manual intervention

### GET `/transfers`
List persisted transfer summary records.

Query Parameters:
- `room_name` (optional): Filter by room
- `limit` (optional int, default 50)

Response:
```json
{
  "transfers": [
    {
      "id": "b1a0d5b0-0e5d-4a9c-8e76-5fd4d0c6b9e2",
      "room_name": "unknown",
      "agent_a": "unknown",
      "agent_b": null,
      "summary": "Mock Summary: ...",
      "call_context": "Customer ...",
      "created_at": 1737050123.123
    }
  ]
}
```

### GET `/transfers/{id}`
Retrieve a single persisted transfer summary.

Response:
```json
{
  "id": "b1a0d5b0-0e5d-4a9c-8e76-5fd4d0c6b9e2",
  "room_name": "unknown",
  "agent_a": "unknown",
  "agent_b": null,
  "summary": "Mock Summary: ...",
  "call_context": "Customer ...",
  "created_at": 1737050123.123
}
```

Errors:
- 404 if the record does not exist.

### POST `/ai-voice`
Generate speech (WAV) from text. If `GROQ_API_KEY` is set and not forced to mock, it first generates a response via Groq, then synthesizes locally with pyttsx3.

Request Body:
```json
{ "prompt": "Say hello" }
```
Response: audio/wav stream

### AI Agent Controls

Start, talk, and stop a lightweight AI agent participant. The system supports multiple agent modes:

**Voice AI Agent (Full Conversational):**
- Real-time Speech-to-Text (STT) using OpenAI Whisper
- Large Language Model (LLM) conversation using OpenAI GPT
- Text-to-Speech (TTS) using OpenAI voices
- Natural voice conversations with customers
- Intelligent responses and context awareness

**Basic Agent (TTS Only):**
- Text-to-speech output using local pyttsx3
- Agent can respond to programmatic prompts
- Real audio publishing via LiveKit RTC

**Mock Agent (Testing):**
- Validates control surface without media
- Logs all commands for debugging

**Agent Endpoints:**
- POST `/agent/start`
  - Body: `{ "room_name": "support-1", "identity": "ai-agent" }`
  - Ensures room exists then starts agent session for the room
- POST `/agent/say`
  - Body: `{ "room_name": "support-1", "text": "Welcome to support!" }`
  - Sends a prompt to the agent (voice AI responds naturally, basic agent uses TTS)
- POST `/agent/stop`
  - Body: `{ "room_name": "support-1" }`
  - Stops the agent session for that room

**Agent Configuration:**
- `ENABLE_AGENT_MOCK=1`: Use mock agent (default for testing)
- `ENABLE_VOICE_AI=1`: Enable full voice AI agent (requires OpenAI API key)
- `ENABLE_AGENT_MOCK=0`: Enable basic real agent with TTS

## 🔄 Warm Transfer Workflow

### Step 1: Initial Call Setup
1. **Customer** joins a room using any room name
2. **Agent A** joins the same room to assist the customer

### Step 2: Transfer Initiation
1. **Agent A** clicks "Warm Transfer" button
2. System prompts for call context input
3. **Agent A** describes the current situation and customer needs
4. System calls Groq API to generate a concise summary

### Step 3: Agent Briefing
1. **Agent A** reviews the AI-generated summary
2. **Agent A** connects with **Agent B** separately (via phone, chat, etc.)
3. **Agent A** shares the summary with **Agent B**
4. **Agent B** prepares to take over the call

### Step 4: Transfer Completion
1. **Agent B** joins the original room with the customer
2. **Agent A** clicks "Complete Transfer"
3. System removes **Agent A** from the room
4. **Agent B** continues the conversation with the customer

## 🛠️ Development

### Project Structure
```
warm-call/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .env.example        # Environment template
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx    # Main landing page
│   │   │   └── layout.tsx  # App layout
│   │   └── components/
│   │       └── CallRoom.tsx # Video conference component
│   ├── package.json        # Node.js dependencies
│   └── .env.example       # Environment template
├── .gitignore             # Git ignore rules
├── start-dev.bat         # Windows startup script
└── start-dev.sh          # Unix startup script
```

### Key Technologies

**Backend:**
- **FastAPI**: Modern, fast web framework for Python APIs
- **LiveKit Server SDK**: Real-time communication infrastructure
- **Groq**: Fast LLM inference for call summaries
- **Uvicorn**: ASGI server for production deployment

**Frontend:**
- **Next.js 15**: React framework with app directory structure
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **LiveKit Components**: Pre-built React components for video calls

### Environment Variables

**Backend (`backend/.env`):**
```env
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret  
LIVEKIT_URL=wss://your-livekit-server.com
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key  # Required for Voice AI Agent
HOST=127.0.0.1
PORT=8000
FORCE_MOCK_GROQ=0 # Set to 1 to force mock summaries (optional)
PERSIST_DB_PATH= # Optional custom path for SQLite persistence
ENABLE_AGENT_MOCK=1 # Set to 0 to enable real agent implementation (requires livekit-agents)
ENABLE_VOICE_AI=0 # Set to 1 to enable full voice AI agent (requires OpenAI API key)
```

**Frontend (`frontend/.env.local`):**
```env
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-server.com
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 🔧 Configuration

### LiveKit Setup
1. Create account at [LiveKit Cloud](https://cloud.livekit.io)
2. Generate API key and secret
3. Note your WebSocket URL
4. Update environment variables

### Groq Setup
1. Sign up at [Groq](https://groq.com)
2. Generate API key
3. Update `GROQ_API_KEY` in backend environment

### OpenAI Setup (for Voice AI Agent)
1. Sign up at [OpenAI](https://platform.openai.com)
2. Generate API key
3. Update `OPENAI_API_KEY` in backend environment
4. Set `ENABLE_VOICE_AI=1` to enable voice AI capabilities

## 🧪 Testing the Application

### LiveKit Integration Testing

The backend includes comprehensive test scripts to validate LiveKit integration:

**Test Token Generation:**
```bash
cd backend
python test_token_only.py
```
✅ Tests official LiveKit SDK token generation  
✅ Validates API credentials  
✅ Confirms token format and length  

**Test API Integration:**
```bash
cd backend
python test_api_integration.py
```
✅ Tests room creation and listing  
✅ Validates API connectivity  
✅ Confirms participant management capabilities  

**Test Full Backend:**
```bash
cd backend
python test_livekit.py
```
✅ Tests all API endpoints  
✅ Validates token endpoint responses  
✅ Confirms room management functionality  

### Manual Testing Workflow

1. **Start both servers** using provided scripts
2. **Open three browser tabs** to http://localhost:3000

**Tab 1 - Customer:**
- Name: "Customer John"  
- Room: "support-room-1"
- Click "Join Room"

**Tab 2 - Agent A:**
- Name: "Agent A"
- Room: "support-room-1" 
- Click "Join Room"

**Tab 3 - Agent B:**
- Name: "Agent B"
- Room: "support-room-1"
- Wait for transfer completion

3. **Simulate Transfer:**
   - In Agent A tab, click "Warm Transfer"
   - Enter call context: "Customer needs help with account billing"
   - Review generated summary
   - Click "Complete Transfer"
   - Agent A will be removed from the call
   - Agent B can now join and continue
  - (Optional) Query `/transfers` endpoint to view persisted summary

## 🚀 Production Deployment

### Backend Deployment
```bash
# Using Docker
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Deploy to Vercel, Netlify, or similar
npm run start
```

## 🔍 Troubleshooting

### Common Issues

**1. LiveKit Connection Failed**
- Verify `LIVEKIT_URL` is correct WebSocket URL
- Check API key and secret are valid
- Ensure LiveKit server is accessible

**2. Groq API Errors** 
- Verify `GROQ_API_KEY` is set correctly
- Check Groq service status
- Review API rate limits

**3. CORS Issues**
- Backend includes CORS middleware for localhost:3000
- Update CORS origins for production deployment

**4. Token Generation Fails**
- Check all LiveKit environment variables
- Verify room name and identity are provided
- Review server logs for detailed errors

**5. Backend Dependencies**
If you encounter import errors, ensure all dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

Key backend packages:
- `livekit-api==1.0.5` - Official LiveKit Python SDK
- `fastapi==0.104.1` - Web framework
- `groq==0.4.1` - AI API client
- `python-dotenv==1.0.0` - Environment management

## 📚 Additional Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Groq API Documentation](https://console.groq.com/docs)

## 🎉 Success!

Your Warm Transfer application is now fully functional with:
- ✅ Official LiveKit SDK integration
- ✅ Real-time video/audio communication
- ✅ AI-powered call summaries
- ✅ Mock summary fallback for offline / keyless development
- ✅ Proper participant management
- ✅ Clean transfer workflows
- ✅ Persistent storage of generated summaries
- ✅ Comprehensive testing suite

Enjoy seamless warm transfers with live audio calls! 🚀

### Debug Mode
Enable debug logging in backend:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes with proper git commits
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review LiveKit documentation
- Check Groq API documentation
- Create an issue in the repository

---

**Built with ❤️ using LiveKit, FastAPI, Next.js, and Groq**