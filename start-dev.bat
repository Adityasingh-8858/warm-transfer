@echo off
echo Starting Warm Transfer Application...

echo.
echo Starting backend server...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
start "Backend Server" cmd /k "uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo.
echo Starting frontend server...
cd ..\frontend
call npm install
start "Frontend Server" cmd /k "npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Close the command windows to stop the servers.
pause