#!/bin/bash

# Start backend development server
echo "Starting backend server..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000 &

# Start frontend development server
echo "Starting frontend server..."
cd ../frontend
npm install
npm run dev &

echo "Both servers are starting..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers"

wait