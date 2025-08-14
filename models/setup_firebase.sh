#!/bin/bash

echo "🚀 Setting up Firebase Functions for ECG Model System..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "📦 Installing Firebase CLI..."
    npm install -g firebase-tools
else
    echo "✅ Firebase CLI version: $(firebase --version)"
fi

# Navigate to firebase directory
cd firebase

# Install Firebase Functions dependencies
echo "📦 Installing Firebase Functions dependencies..."
cd functions
npm install
cd ..

# Initialize Firebase project (if not already done)
if [ ! -f ".firebaserc" ] || [ ! -f "firebase.json" ]; then
    echo "🔧 Initializing Firebase project..."
    firebase init functions --project=your-ecg-project-id --yes
else
    echo "✅ Firebase project already initialized"
fi

echo ""
echo "🎯 Firebase Functions setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .firebaserc with your actual Firebase project ID"
echo "2. Update server.py with your Firebase endpoints"
echo "3. Start Firebase emulator: firebase emulators:start"
echo "4. Test the system: python3 test_system.py"
echo ""
echo "To start the system:"
echo "./start_system_firebase.sh" 