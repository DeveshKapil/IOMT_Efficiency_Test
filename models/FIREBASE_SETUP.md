# Firebase Functions Setup Guide for ECG Model System

This guide will help you set up and run the ECG Model System using Firebase Functions instead of AWS Lambda.

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Make scripts executable
chmod +x setup_firebase.sh start_system_firebase.sh deploy_firebase.sh

# Run Firebase setup
./setup_firebase.sh
```

### 2. Start the System
```bash
# Start all services (Firebase emulator, receiver, frontend)
./start_system_firebase.sh
```

### 3. Test the System
```bash
# Test all components
python3 test_system.py
```

### 4. Start Data Processing
```bash
# Start sending data through Firebase Functions
python3 server.py
```

## 📋 Prerequisites

- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Python 3.8+** - Should already be installed
- **Firebase Account** - [Create here](https://firebase.google.com/)
- **Git** - For version control

## 🔧 Detailed Setup Steps

### Step 1: Install Dependencies

#### Install Node.js and npm
```bash
# Check if Node.js is installed
node --version
npm --version

# If not installed, install Node.js 18+ from https://nodejs.org/
```

#### Install Firebase CLI
```bash
npm install -g firebase-tools
```

### Step 2: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Create a project"**
3. Enter project name: `ecg-model-system` (or your preferred name)
4. Enable Google Analytics (optional)
5. Click **"Create project"**
6. Note your **Project ID** (you'll need this later)

### Step 3: Configure Firebase Project

#### Update Project Configuration
Edit `firebase/.firebaserc`:
```json
{
  "projects": {
    "default": "your-actual-project-id"
  }
}
```

Replace `your-actual-project-id` with your Firebase project ID.

#### Update Server Configuration
Edit `server.py` and update the Firebase endpoints:
```python
# For local development with Firebase emulator:
FIREBASE_ENDPOINT_1 = "http://localhost:5001/your-project-id/us-central1/processNonCompressed"
FIREBASE_ENDPOINT_2 = "http://localhost:5001/your-project-id/us-central1/processCompressed"

# For production (after deployment):
# FIREBASE_ENDPOINT_1 = "https://us-central1-your-project-id.cloudfunctions.net/processNonCompressed"
# FIREBASE_ENDPOINT_2 = "https://us-central1-your-project-id.cloudfunctions.net/processCompressed"
```

### Step 4: Install Dependencies

#### Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

#### Install Firebase Functions Dependencies
```bash
cd firebase/functions
npm install
cd ../..
```

#### Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 5: Login to Firebase

```bash
firebase login
```

Follow the browser authentication process.

## 🏃‍♂️ Running the System

### Option 1: Use the Startup Script (Recommended)
```bash
./start_system_firebase.sh
```

This script will:
- Start Firebase Functions emulator on port 5001
- Start the Model Receiver on port 5000
- Start the React Frontend on port 3000
- Open Firebase UI on port 4000

### Option 2: Manual Start

#### Start Firebase Emulator
```bash
cd firebase
firebase emulators:start --only functions
```

#### Start Receiver (in new terminal)
```bash
python3 receiver.py
```

#### Start Frontend (in new terminal)
```bash
cd frontend
npm start
```

## 🧪 Testing the System

### Run All Tests
```bash
python3 test_system.py
```

### Test Individual Components

#### Test Firebase Functions
```bash
# Test endpoint
curl http://localhost:5001/your-project-id/us-central1/test

# Health check
curl http://localhost:5001/your-project-id/us-central1/health
```

#### Test Receiver
```bash
curl http://localhost:5000/health
```

#### Test Frontend
Open http://localhost:3000 in your browser

## 📊 System Architecture

```
CSV Data → Server → Firebase Functions → Receiver → Models → Frontend
                ↓
        Random Row Selection
                ↓
        Timestamp Addition
                ↓
    ┌─────────────────┬─────────────────┐
    │                 │                 │
Non-compressed    Compressed      Compressed
    │                 │                 │
    ↓                 ↓                 ↓
Firebase Func    Firebase Func    Firebase Func
(processNon)     (processComp)    (processComp)
    │                 │                 │
    ↓                 ↓                 ↓
Receiver         Receiver         Receiver
(Standard        (Decompressed    (Zlib Models)
 Models)          + Standard)      + Standard)
    │                 │                 │
    └─────────────────┼─────────────────┘
                      ↓
                Frontend Dashboard
```

## 🌐 Firebase Functions Endpoints

### Local Development (Emulator)
- **Non-compressed**: `http://localhost:5001/your-project-id/us-central1/processNonCompressed`
- **Compressed**: `http://localhost:5001/your-project-id/us-central1/processCompressed`
- **Health**: `http://localhost:5001/your-project-id/us-central1/health`
- **Test**: `http://localhost:5001/your-project-id/us-central1/test`

### Production (After Deployment)
- **Non-compressed**: `https://us-central1-your-project-id.cloudfunctions.net/processNonCompressed`
- **Compressed**: `https://us-central1-your-project-id.cloudfunctions.net/processCompressed`
- **Health**: `https://us-central1-your-project-id.cloudfunctions.net/health`

## 🚀 Deployment to Production

### Deploy Firebase Functions
```bash
./deploy_firebase.sh
```

### Update Server Configuration
After deployment, update `server.py` with production endpoints:
```python
# Production endpoints
FIREBASE_ENDPOINT_1 = "https://us-central1-your-project-id.cloudfunctions.net/processNonCompressed"
FIREBASE_ENDPOINT_2 = "https://us-central1-your-project-id.cloudfunctions.net/processCompressed"
```

## 🔍 Monitoring and Debugging

### Firebase Functions Logs
```bash
# View logs in Firebase Console
firebase functions:log

# Or view in Firebase Console UI
firebase emulators:start --only functions
# Then open http://localhost:4000
```

### Receiver Logs
Check the terminal where you started the receiver for model processing logs.

### Frontend Logs
Check the browser console for any JavaScript errors.

## 🛠️ Troubleshooting

### Common Issues

#### 1. Firebase Functions Not Starting
```bash
# Check if ports are available
lsof -i :5001
lsof -i :4000

# Kill processes if needed
lsof -ti:5001 | xargs kill -9
lsof -ti:4000 | xargs kill -9
```

#### 2. Connection Refused Errors
- Ensure Firebase emulator is running
- Check if receiver is accessible from Firebase Functions
- Verify CORS settings

#### 3. Model Loading Errors
- Ensure all `.joblib` files are in the project root
- Check file permissions
- Verify model compatibility

#### 4. Port Already in Use
```bash
# Kill processes on specific ports
lsof -ti:5000 | xargs kill -9  # Receiver
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:5001 | xargs kill -9  # Firebase Functions
lsof -ti:4000 | xargs kill -9  # Firebase UI
```

### Debug Mode

#### Enable Firebase Debug Logging
```bash
export DEBUG=firebase:*
firebase emulators:start --only functions
```

#### Enable Python Debug Logging
Edit `server.py` and `receiver.py`:
```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## 📈 Performance Optimization

### Firebase Functions
- Increase memory allocation in `firebase.json`
- Use connection pooling for external requests
- Implement caching strategies

### Receiver
- Optimize model inference
- Use batch processing for multiple requests
- Implement result caching

### Frontend
- Reduce API call frequency
- Implement data pagination
- Use WebSocket for real-time updates

## 🔒 Security Considerations

### Firebase Functions
- Implement authentication
- Validate input data
- Use environment variables for sensitive data
- Enable HTTPS (automatic in production)

### Receiver
- Implement API key authentication
- Rate limiting
- Input validation
- CORS configuration

## 📚 Additional Resources

- [Firebase Functions Documentation](https://firebase.google.com/docs/functions)
- [Firebase CLI Reference](https://firebase.google.com/docs/cli)
- [Firebase Emulator Guide](https://firebase.google.com/docs/emulator-suite)
- [Node.js Documentation](https://nodejs.org/docs/)

## 🆘 Getting Help

### Check Logs
1. Firebase Functions logs in Firebase Console
2. Receiver logs in terminal
3. Frontend logs in browser console

### Common Commands
```bash
# Check system status
./start_system_firebase.sh

# Test system
python3 test_system.py

# Deploy to production
./deploy_firebase.sh

# View Firebase logs
firebase functions:log
```

### Support
1. Check this troubleshooting guide
2. Review Firebase documentation
3. Check GitHub issues
4. Contact the development team

---

**Happy coding! 🎉**

Your ECG Model System is now running with Firebase Functions! 

## 🔄 **Complete Data Flow Architecture**

### **1. Data Generation & Sending (Server)**
```
CSV File → Random Row Selection → Data Processing → Firebase Functions
```

**Step-by-step:**
1. **CSV Loading**: `server.py` loads `exported_data.csv` with ECG data
2. **Random Selection**: Picks a random row (187 features) every second
3. **Data Preparation**: 
   - **Non-compressed**: Raw data (187 features) → JSON payload
   - **Compressed**: Raw data → zlib compression → base64 encoding → JSON payload
4. **Sending**: HTTP POST to Firebase Functions endpoints

### **2. Firebase Functions (Cloud Layer)**
```
Server → Firebase Functions → Receiver
```

**Two Endpoints:**
- **`/processNonCompressed`**: Receives raw data, forwards to receiver
- **`/processCompressed`**: Receives compressed data, forwards to receiver

**Firebase Functions act as:**
- **Load balancer**: Distributes requests
- **Middleware**: Handles CORS, validation, error handling
- **Forwarder**: Routes data to the receiver

### **3. Model Processing (Receiver)**
```
Firebase → Receiver → Multiple Model Pipelines → Results Storage
```

**For Non-compressed Data:**
```
Raw Data (187 features) → Standard Models → Results
├── KNN Model
├── Random Forest Model  
├── XGBoost Model
├── SVM Model (with scaler)
└── Logistic Regression Model (with scaler)
```

**For Compressed Data:**
```
Compressed Data → Decompression → Two Processing Paths
├── Path 1: Decompressed Data (187 features) → Standard Models → Results
└── Path 2: Re-compressed Data (667 features) → Zlib Models → Results
    ├── KNN Zlib Model
    ├── Random Forest Zlib Model
    ├── XGBoost Zlib Model
    ├── SVM Zlib Model (with zlib scaler)
    └── Logistic Regression Zlib Model (with zlib scaler)
```

### **4. Results Storage & Retrieval**
```
Model Results → Memory Buffer → Frontend API
```

**Storage:**
- Results stored in `results_buffer` (last 100 results)
- Each result includes: predictions, timing, timestamps, data type
- Thread-safe access with locks

**API Endpoints:**
- `/get_results`: Returns all stored results
- `/health`: Health check endpoint

### **5. Frontend Display (React Dashboard)**
```
Receiver API → React App → Real-time Visualization
```

**Data Fetching:**
- React app polls `/get_results` every 2 seconds
- Processes results for different visualizations

**Dashboard Components:**
1. **ECG Data Stream**: Real-time ECG signal plotting
2. **Model Performance**: Bar chart of average processing times
3. **Real-time Timing**: Line chart comparing decompressed vs zlib processing times
4. **Latest Predictions**: Cards showing all model outputs with timing

## 📊 **Detailed Data Flow Diagram**

```
<code_block_to_apply_changes_from>
```

## 🔄 **Real-time Data Flow Example**

**Timeline (every 1 second):**

```
T=0s: Server selects row 1234 from CSV
T=0.1s: Server compresses data, sends to Firebase
T=0.2s: Firebase forwards to receiver
T=0.3s: Receiver processes through all models
T=0.4s: Results stored in buffer
T=0.5s: Frontend fetches results (every 2s)
T=0.6s: Dashboard updates with new data
```

## 📈 **Data Types & Processing**

| Data Type | Features | Models Used | Purpose |
|-----------|----------|-------------|---------|
| **Non-compressed** | 187 | Standard Models | Baseline performance |
| **Decompressed** | 187 | Standard Models | Compression overhead comparison |
| **Zlib** | 667 | Zlib Models | Specialized compressed data models |

## 🎯 **Key Benefits of This Architecture**

1. **Scalability**: Firebase Functions can handle multiple requests
2. **Reliability**: Error handling at each layer
3. **Real-time**: Continuous data flow with live updates
4. **Comparison**: Three different processing paths for analysis
5. **Monitoring**: Comprehensive logging and health checks

This architecture ensures your ECG data flows smoothly from the CSV file all the way to the real-time dashboard, with multiple processing paths for comprehensive analysis! 🚀 