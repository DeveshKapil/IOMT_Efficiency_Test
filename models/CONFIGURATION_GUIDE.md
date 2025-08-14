# 🔧 ECG Model System - Centralized Configuration Guide

## Overview

The ECG Model System now uses a **centralized configuration system** that automatically detects your IP addresses and manages all URLs, ports, and endpoints from a single location. This eliminates the need to manually update multiple files when your network configuration changes.

## 🎯 Key Features

- **🔄 Auto-Detection**: Automatically detects local IP, public IP, and ngrok URLs
- **📍 Single Point of Control**: All configuration in one file (`config.py`)
- **🌐 Dynamic URLs**: URLs update automatically based on network changes
- **🔌 Port Management**: Centralized port configuration
- **📊 Status Monitoring**: Easy system status checking

## 📁 Configuration Files

### 1. `config.py` - Main Configuration
The central configuration file that manages all system settings.

**Key Properties:**
- `local_ip`: Automatically detected local IP address
- `public_ip`: Automatically detected public IP address  
- `ngrok_url`: Automatically detected ngrok tunnel URL
- `receiver_url`: Smart URL that prefers ngrok, falls back to local IP
- All Firebase endpoints and ports

### 2. `firebase/functions/config.js` - Firebase Configuration
Manages Firebase Functions configuration with dynamic receiver URL detection.

### 3. Scripts
- `start_system_auto.sh`: Auto-starts system with IP detection
- `stop_system.sh`: Stops all system components
- `check_status.sh`: Shows current system status

## 🚀 Quick Start

### 1. Check Current Configuration
```bash
python3 config.py
```

### 2. Start the System
```bash
./start_system_auto.sh
```

### 3. Check Status
```bash
./check_status.sh
```

### 4. Stop the System
```bash
./stop_system.sh
```

## 🔧 Configuration Options

### Ports (in `config.py`)
```python
RECEIVER_PORT = 5000
FRONTEND_PORT = 3000
FIREBASE_EMULATOR_PORT = 5002
FIREBASE_UI_PORT = 4001
NGROK_API_PORT = 4040
```

### Firebase Settings (in `config.py`)
```python
FIREBASE_PROJECT_ID = "ecg-monitoring-system-bb817"
FIREBASE_REGION = "us-central1"
```

### Data Settings (in `config.py`)
```python
DATA_INTERVAL_SECONDS = 1
CSV_FILE_PATH = "exported_data.csv"
COMPRESSED_FEATURES = 667
STANDARD_FEATURES = 187
```

## 🌐 URL Management

The system automatically manages these URLs:

### Receiver URLs
- **Local**: `http://localhost:5000`
- **Public**: `http://{local_ip}:5000` or `{ngrok_url}`

### Frontend URLs
- **Local**: `http://localhost:3000`

### Firebase URLs
- **Cloud**: `https://{region}-{project_id}.cloudfunctions.net`
- **Emulator**: `http://localhost:5002`

### Endpoints
- **Health**: `{firebase_url}/health`
- **Test**: `{firebase_url}/test`
- **Non-compressed**: `{firebase_url}/processNonCompressed`
- **Compressed**: `{firebase_url}/processCompressed`

## 🔄 Auto-Detection Features

### IP Detection
```python
# Local IP detection
local_ip = config.local_ip  # e.g., "172.24.255.55"

# Public IP detection  
public_ip = config.public_ip  # e.g., "106.222.138.233"
```

### Ngrok Detection
```python
# Automatic ngrok URL detection
ngrok_url = config.ngrok_url  # e.g., "https://abc123.ngrok-free.app"
```

### Smart Receiver URL
```python
# Automatically chooses best receiver URL
receiver_url = config.receiver_url  # Prefers ngrok, falls back to local IP
```

## 📊 System Status Commands

### Check All Components
```bash
./check_status.sh
```

### Check Configuration Only
```bash
python3 config.py
```

### Check Specific Components
```bash
# Check receiver
curl http://localhost:5000/health

# Check frontend
curl http://localhost:3000

# Check Firebase Functions
curl https://us-central1-ecg-monitoring-system-bb817.cloudfunctions.net/test
```

## 🔧 Customization

### Change Ports
Edit `config.py`:
```python
RECEIVER_PORT = 5001  # Change receiver port
FRONTEND_PORT = 3001  # Change frontend port
```

### Change Firebase Project
Edit `config.py`:
```python
FIREBASE_PROJECT_ID = "your-new-project-id"
FIREBASE_REGION = "us-west1"  # Change region
```

### Change Data Settings
Edit `config.py`:
```python
DATA_INTERVAL_SECONDS = 5  # Send data every 5 seconds
CSV_FILE_PATH = "your_data.csv"  # Different CSV file
```

## 🛠️ Troubleshooting

### Configuration Issues
1. **Check current config**: `python3 config.py`
2. **Verify IP detection**: Check if local/public IPs are correct
3. **Check ngrok**: Ensure ngrok is running and accessible

### Network Issues
1. **Check ports**: `./check_status.sh`
2. **Verify connectivity**: Test URLs manually
3. **Check firewall**: Ensure ports are not blocked

### Service Issues
1. **Check logs**: 
   - `tail -f models/receiver.log`
   - `tail -f models/server.log`
   - `tail -f frontend/frontend.log`
2. **Restart services**: `./stop_system.sh && ./start_system_auto.sh`

## 📋 Environment Variables

### Firebase Functions (.env)
```bash
RECEIVER_URL=https://your-ngrok-url.ngrok-free.app
LOG_LEVEL=info
REQUEST_TIMEOUT=30000
CORS_ORIGINS=*
```

## 🎯 Benefits

1. **🔄 Zero Manual Updates**: No need to update URLs when network changes
2. **🌐 Automatic Adaptation**: System adapts to different network environments
3. **📊 Easy Monitoring**: Single command to check all components
4. **🔧 Simple Configuration**: All settings in one place
5. **🚀 Quick Deployment**: Automatic deployment with correct URLs

## 📞 Support

If you encounter issues:

1. Run `./check_status.sh` to diagnose problems
2. Check logs in respective `.log` files
3. Verify configuration with `python3 config.py`
4. Restart system with `./stop_system.sh && ./start_system_auto.sh`

---

**🎉 Your ECG Model System is now fully automated with centralized configuration!**
