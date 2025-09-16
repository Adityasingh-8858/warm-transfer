# Warm Transfer Application

A real-time communication system that facilitates warm call transfers between agents using LiveKit and AI-powered call summaries.

## 🎯 Overview

This application enables seamless warm transfers where Agent A can brief Agent B about a customer call before transferring the conversation. The system uses LiveKit for real-time video/audio communication and Groq LLM for generating intelligent call summaries.

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI** framework for REST API endpoints
- **LiveKit Server SDK** for room and participant management
- **Groq API** integration for AI-powered call summaries
- **Environment-based configuration** for security

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
Generate LiveKit access token for room participation.

**Query Parameters:**
- `room_name` (string): Target room name
- `identity` (string): Participant identity/name

**Response:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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
  "summary": "Customer John Smith is experiencing billing discrepancies on account #12345. Previous agent confirmed the issue and initiated a refund request. Next steps: Complete refund processing and update customer."
}
```

### POST `/complete-transfer`
Finalize transfer by removing Agent A from the original room.

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
HOST=127.0.0.1
PORT=8000
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

## 🧪 Testing the Application

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