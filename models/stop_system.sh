#!/bin/bash

# ECG Model System Stop Script
# This script stops all components of the ECG Model System

echo "🛑 Stopping ECG Model System..."

# Function to check if a process is running
is_running() {
    local process_name=$1
    if pgrep -f "$process_name" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to stop a process gracefully
stop_process() {
    local process_name=$1
    local display_name=$2
    
    if is_running "$process_name"; then
        echo "🔄 Stopping $display_name..."
        pkill -f "$process_name"
        sleep 2
        
        # Force kill if still running
        if is_running "$process_name"; then
            echo "⚠️ Force stopping $display_name..."
            pkill -9 -f "$process_name"
            sleep 1
        fi
        
        if is_running "$process_name"; then
            echo "❌ Failed to stop $display_name"
            return 1
        else
            echo "✅ $display_name stopped"
            return 0
        fi
    else
        echo "ℹ️ $display_name is not running"
        return 0
    fi
}

# Function to stop processes on specific ports
stop_port() {
    local port=$1
    local display_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "🔄 Stopping $display_name on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "❌ Failed to stop $display_name on port $port"
            return 1
        else
            echo "✅ $display_name on port $port stopped"
            return 0
        fi
    else
        echo "ℹ️ $display_name on port $port is not running"
        return 0
    fi
}

# Stop all components
echo "=========================================="
echo "🛑 Stopping ECG Model System Components"
echo "=========================================="

# Stop Python processes
stop_process "python3 server.py" "Data Server"
stop_process "python3 receiver.py" "Model Receiver"

# Stop Node.js processes
stop_process "npm start" "React Frontend"
stop_process "node.*frontend" "Frontend Server"

# Stop ngrok
stop_process "ngrok" "Ngrok Tunnel"

# Stop Firebase emulator (if running)
stop_process "firebase.*emulator" "Firebase Emulator"

# Stop processes on specific ports
stop_port 5000 "Receiver"
stop_port 3000 "Frontend"
stop_port 4040 "Ngrok API"
stop_port 5002 "Firebase Emulator"
stop_port 4001 "Firebase UI"

# Clean up any remaining processes
echo ""
echo "🧹 Cleaning up remaining processes..."

# Kill any remaining Python processes related to our system
pkill -f "python.*server" 2>/dev/null
pkill -f "python.*receiver" 2>/dev/null

# Kill any remaining Node processes related to our system
pkill -f "node.*frontend" 2>/dev/null
pkill -f "npm.*start" 2>/dev/null

# Kill any remaining ngrok processes
pkill -f "ngrok" 2>/dev/null

# Wait a moment for processes to fully stop
sleep 2

# Final verification
echo ""
echo "🔍 Final Status Check:"
echo "======================"

# Check if any components are still running
components_running=false

if is_running "python3 server.py"; then
    echo "❌ Data Server is still running"
    components_running=true
fi

if is_running "python3 receiver.py"; then
    echo "❌ Model Receiver is still running"
    components_running=true
fi

if is_running "npm start"; then
    echo "❌ React Frontend is still running"
    components_running=true
fi

if is_running "ngrok"; then
    echo "❌ Ngrok is still running"
    components_running=true
fi

# Check ports
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Port 5000 is still in use"
    components_running=true
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Port 3000 is still in use"
    components_running=true
fi

if lsof -Pi :4040 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Port 4040 is still in use"
    components_running=true
fi

if [ "$components_running" = false ]; then
    echo "✅ All components stopped successfully"
    echo ""
    echo "🎉 ECG Model System has been completely stopped!"
    echo ""
    echo "📊 Log files are preserved:"
    echo "   - models/server.log"
    echo "   - models/receiver.log"
    echo "   - frontend/frontend.log"
    echo "   - ngrok.log"
    echo ""
    echo "🚀 To restart the system: ./start_system_auto.sh"
else
    echo ""
    echo "⚠️ Some components may still be running"
    echo "You may need to manually stop them or restart your system"
fi

echo ""
echo "=========================================="
