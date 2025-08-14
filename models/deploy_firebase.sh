#!/bin/bash

echo "🚀 Deploying Firebase Functions to production..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI is not installed. Please run ./setup_firebase.sh first."
    exit 1
fi

# Check if user is logged in to Firebase
if ! firebase projects:list &> /dev/null; then
    echo "🔐 Please login to Firebase first:"
    firebase login
fi

# Navigate to firebase directory
cd firebase

# Check if .firebaserc has a valid project ID
PROJECT_ID=$(grep -o '"default": "[^"]*"' .firebaserc | cut -d'"' -f4)
if [ "$PROJECT_ID" = "your-ecg-project-id" ]; then
    echo "❌ Please update .firebaserc with your actual Firebase project ID first."
    echo "Current project ID: $PROJECT_ID"
    exit 1
fi

echo "📋 Deploying to Firebase project: $PROJECT_ID"

# Deploy functions
echo "📦 Deploying Firebase Functions..."
firebase deploy --only functions

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Firebase Functions deployed successfully!"
    echo ""
    echo "📝 Update your server.py with these production endpoints:"
    echo "FIREBASE_ENDPOINT_1 = \"https://us-central1-$PROJECT_ID.cloudfunctions.net/processNonCompressed\""
    echo "FIREBASE_ENDPOINT_2 = \"https://us-central1-$PROJECT_ID.cloudfunctions.net/processCompressed\""
    echo ""
    echo "🌐 Your functions are now available at:"
    echo "   Non-compressed: https://us-central1-$PROJECT_ID.cloudfunctions.net/processNonCompressed"
    echo "   Compressed: https://us-central1-$PROJECT_ID.cloudfunctions.net/processCompressed"
    echo "   Health: https://us-central1-$PROJECT_ID.cloudfunctions.net/health"
    echo ""
    echo "🔧 To test production endpoints, update server.py and run:"
    echo "python3 server.py"
else
    echo "❌ Firebase Functions deployment failed!"
    exit 1
fi

cd .. 