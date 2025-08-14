#!/bin/bash

echo "🚀 Starting ECG Model System with Firebase Functions..."

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use"
        return 1
    else
        echo "Port $1 is available"
        return 0
    fi
}

# Function to kill process on a port
kill_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Killing process on port $1"
        lsof -ti:$1 | xargs kill -9
        sleep 2
    fi
}

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
kill_port 5000  # Receiver
kill_port 3000  # Frontend
kill_port 5002  # Firebase Functions emulator
kill_port 4001  # Firebase UI

# Check if Python dependencies are installed
echo "🐍 Checking Python dependencies..."
if ! python3 -c "import pandas, numpy, sklearn, xgboost, joblib, flask, flask_cors, requests" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI is not installed. Please run ./setup_firebase.sh first."
    exit 1
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Check if Firebase Functions dependencies are installed
if [ ! -d "firebase/functions/node_modules" ]; then
    echo "📦 Installing Firebase Functions dependencies..."
    cd firebase/functions
    npm install
    cd ../..
fi

# Start Firebase emulator in background
echo "🔥 Starting Firebase Functions emulator on port 5002..."
cd firebase
firebase emulators:start --only functions &
FIREBASE_PID=$!
cd ..
sleep 8

# Check if Firebase emulator started successfully
if ! check_port 5002; then
    echo "❌ Failed to start Firebase emulator"
    exit 1
fi

# Start the receiver (Flask server) in background
echo "📡 Starting Model Receiver on port 5000..."
python3 receiver.py &
RECEIVER_PID=$!
sleep 3

# Check if receiver started successfully
if ! check_port 5000; then
    echo "❌ Failed to start receiver"
    exit 1
fi

# Start the frontend in background
echo "🌐 Starting React Frontend on port 3000..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..
sleep 5

# Check if frontend started successfully
if ! check_port 3000; then
    echo "❌ Failed to start frontend"
    exit 1
fi

echo ""
echo "=========================================="
echo "🎉 ECG Model System Started Successfully!"
echo "=========================================="
echo "Firebase Functions: http://localhost:5002"
echo "Model Receiver: http://localhost:5000"
echo "Frontend Dashboard: http://localhost:3000"
echo "Firebase UI: http://localhost:4001"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $RECEIVER_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill $FIREBASE_PID 2>/dev/null
    kill_port 5000
    kill_port 3000
    kill_port 5002
    kill_port 4001
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Keep script running
echo "🔄 System is running. Press Ctrl+C to stop."
echo ""
echo "📊 To test the system, run: python3 test_system.py"
echo "📝 To start sending data, run: python3 server.py"
echo ""

wait 