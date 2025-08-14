#!/bin/bash

# ECG Model System Auto-Start Script
# This script automatically detects IP addresses and starts all components

echo "🚀 Starting ECG Model System with Auto-Detection..."

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Function to kill existing processes
kill_existing() {
    echo "🔄 Stopping existing processes..."
    pkill -f "python3 server.py" 2>/dev/null
    pkill -f "python3 receiver.py" 2>/dev/null
    pkill -f "ngrok" 2>/dev/null
    pkill -f "npm start" 2>/dev/null
    sleep 2
}

# Function to print configuration
print_config() {
    echo "🔧 Current Configuration:"
    python3 config.py
    echo ""
}

# Kill existing processes
kill_existing

# Print current configuration
print_config

# Check ports
echo "🔍 Checking port availability..."
check_port 5000 || exit 1
check_port 3000 || exit 1
check_port 4040 || exit 1

# Start ngrok for receiver exposure
echo "🌐 Starting ngrok tunnel for receiver..."
ngrok http 5000 --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!
echo "✅ Ngrok started with PID: $NGROK_PID"

# Wait for ngrok to start
echo "⏳ Waiting for ngrok to initialize..."
sleep 5

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('tunnels'):
        print(data['tunnels'][0]['public_url'])
    else:
        print('')
except:
    print('')
")

if [ -n "$NGROK_URL" ]; then
    echo "✅ Ngrok URL: $NGROK_URL"
else
    echo "❌ Failed to get ngrok URL"
    exit 1
fi

# Update Firebase Functions environment
echo "🔧 Updating Firebase Functions configuration..."
cd firebase/functions
echo "RECEIVER_URL=$NGROK_URL" > .env
echo "LOG_LEVEL=info" >> .env
echo "REQUEST_TIMEOUT=30000" >> .env
echo "CORS_ORIGINS=*" >> .env
cd ..

# Deploy Firebase Functions
echo "☁️ Deploying Firebase Functions..."
firebase deploy --only functions --non-interactive
cd ..

# Wait for deployment
echo "⏳ Waiting for Firebase Functions deployment..."
sleep 10

# Start receiver
echo "🧠 Starting Model Receiver..."
nohup python3 receiver.py > receiver.log 2>&1 &
RECEIVER_PID=$!
echo "✅ Receiver started with PID: $RECEIVER_PID"

# Wait for receiver to start
echo "⏳ Waiting for receiver to initialize..."
sleep 5

# Check receiver health
echo "🏥 Checking receiver health..."
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ Receiver is healthy"
else
    echo "❌ Receiver health check failed"
    exit 1
fi

# Start frontend
echo "🎨 Starting React Frontend..."
cd frontend
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started with PID: $FRONTEND_PID"
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 5

# Check frontend
echo "🌐 Checking frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend check failed"
    exit 1
fi

# Start server
echo "📡 Starting Data Server..."
nohup python3 server.py > server.log 2>&1 &
SERVER_PID=$!
echo "✅ Server started with PID: $SERVER_PID"

# Wait for server to start
echo "⏳ Waiting for server to initialize..."
sleep 5

# Final status check
echo ""
echo "🎉 System Status:"
echo "=================="
echo "🌐 Ngrok URL: $NGROK_URL"
echo "🧠 Receiver: http://localhost:5000 (PID: $RECEIVER_PID)"
echo "🎨 Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "📡 Server: Running (PID: $SERVER_PID)"
echo "☁️ Firebase: Deployed to cloud"
echo ""
echo "🔗 Access your dashboard at: http://localhost:3000"
echo ""
echo "📊 To monitor logs:"
echo "   Receiver: tail -f models/receiver.log"
echo "   Server: tail -f models/server.log"
echo "   Frontend: tail -f frontend/frontend.log"
echo "   Ngrok: tail -f ngrok.log"
echo ""
echo "🛑 To stop all services: ./stop_system.sh"
echo ""

# Test the system
echo "🧪 Running system test..."
sleep 5
python3 test_system.py

echo ""
echo "✅ ECG Model System is now running with auto-detected configuration!"
