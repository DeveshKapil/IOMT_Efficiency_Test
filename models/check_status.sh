#!/bin/bash

# ECG Model System Status Check Script
# This script checks the status of all components

echo "🔍 ECG Model System Status Check"
echo "================================="

# Function to check if a process is running
is_running() {
    local process_name=$1
    if pgrep -f "$process_name" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to check port status
check_port() {
    local port=$1
    local service_name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ $service_name (Port $port): Running"
        return 0
    else
        echo "❌ $service_name (Port $port): Not running"
        return 1
    fi
}

# Function to check service health
check_health() {
    local url=$1
    local service_name=$2
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $service_name: Healthy"
        return 0
    else
        echo "❌ $service_name: Unhealthy"
        return 1
    fi
}

# Check Python processes
echo ""
echo "🐍 Python Processes:"
if is_running "python3 server.py"; then
    echo "✅ Data Server: Running"
else
    echo "❌ Data Server: Not running"
fi

if is_running "python3 receiver.py"; then
    echo "✅ Model Receiver: Running"
else
    echo "❌ Model Receiver: Not running"
fi

# Check Node.js processes
echo ""
echo "🟢 Node.js Processes:"
if is_running "npm start"; then
    echo "✅ React Frontend: Running"
else
    echo "❌ React Frontend: Not running"
fi

if is_running "ngrok"; then
    echo "✅ Ngrok Tunnel: Running"
else
    echo "❌ Ngrok Tunnel: Not running"
fi

# Check ports
echo ""
echo "🔌 Port Status:"
check_port 5000 "Receiver"
check_port 3000 "Frontend"
check_port 4040 "Ngrok API"
check_port 5002 "Firebase Emulator"
check_port 4001 "Firebase UI"

# Check service health
echo ""
echo "🏥 Service Health:"
check_health "http://localhost:5000/health" "Receiver"
check_health "http://localhost:3000" "Frontend"
check_health "http://localhost:4040/api/tunnels" "Ngrok API"

# Check Firebase Functions
echo ""
echo "☁️ Firebase Functions:"
if curl -s "https://us-central1-ecg-monitoring-system-bb817.cloudfunctions.net/test" > /dev/null 2>&1; then
    echo "✅ Firebase Functions: Deployed and accessible"
else
    echo "❌ Firebase Functions: Not accessible"
fi

# Show configuration
echo ""
echo "🔧 Current Configuration:"
python3 config.py

# Show recent data flow
echo ""
echo "📊 Recent Data Flow:"
if curl -s "http://localhost:5000/get_results" > /dev/null 2>&1; then
    result_count=$(curl -s "http://localhost:5000/get_results" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', 0))" 2>/dev/null || echo "0")
    echo "✅ Data flowing: $result_count results processed"
else
    echo "❌ No data flow detected"
fi

echo ""
echo "================================="
