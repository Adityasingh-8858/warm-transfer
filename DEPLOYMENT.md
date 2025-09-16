# Deployment and Testing Guide

## Additional Configuration Files

### Package.json Scripts for Frontend
The frontend includes these useful scripts:
- `npm run dev` - Start development server
- `npm run build` - Build for production  
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Backend Development
For backend development, ensure you have:
1. Python virtual environment activated
2. All dependencies installed from requirements.txt
3. Environment variables configured
4. LiveKit server accessible

## Testing Checklist

### Pre-Testing Setup
- [ ] Backend server running on localhost:8000
- [ ] Frontend server running on localhost:3000
- [ ] LiveKit credentials configured
- [ ] Groq API key configured
- [ ] Browser allows camera/microphone access

### Test Scenario 1: Basic Room Join
1. Open browser to http://localhost:3000
2. Enter name and room name
3. Click "Join Room"
4. Verify video/audio connection

### Test Scenario 2: Warm Transfer Flow
1. Customer joins room "test-room"
2. Agent A joins same room "test-room"  
3. Agent A clicks "Warm Transfer"
4. Agent A enters call context
5. System generates summary
6. Agent A clicks "Complete Transfer"
7. Agent B joins room "test-room"
8. Verify only Customer and Agent B remain

### Production Deployment Notes

#### Backend (FastAPI)
- Use production WSGI server like Gunicorn
- Set up proper environment variables
- Configure CORS for production domains
- Enable HTTPS

#### Frontend (Next.js)
- Run `npm run build` for optimized production build
- Deploy to Vercel, Netlify, or similar platform
- Configure environment variables in deployment platform
- Ensure API URLs point to production backend

## Troubleshooting Common Issues

### LiveKit Connection Issues
- Check WebSocket URL format (should start with wss://)
- Verify API credentials are correct
- Ensure firewall allows WebSocket connections

### API Call Failures
- Check CORS configuration in backend
- Verify backend server is running and accessible
- Check browser developer tools for error messages

### Video/Audio Not Working
- Grant browser permissions for camera/microphone
- Check device availability
- Test on different browsers if needed