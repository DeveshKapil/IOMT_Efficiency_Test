#!/bin/bash

# ECG Model System - Cloud Deployment Script
# This script deploys Firebase Functions to the cloud

echo "🚀 Starting Cloud Deployment for ECG Model System..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Check if user is logged in
if ! firebase projects:list &> /dev/null; then
    echo "❌ Not logged into Firebase. Please login first:"
    firebase login
    exit 1
fi

# Get your public IP address
echo "🌐 Getting your public IP address..."
PUBLIC_IP=$(curl -s ifconfig.me)
echo "Your public IP: $PUBLIC_IP"

# Set environment variables for Firebase Functions
echo "🔧 Setting up environment variables..."
cd firebase

# Set the receiver URL to your public IP
firebase functions:config:set receiver.url="http://$PUBLIC_IP:5000"

# Deploy Firebase Functions
echo "📦 Deploying Firebase Functions to cloud..."
firebase deploy --only functions

if [ $? -eq 0 ]; then
    echo "✅ Firebase Functions deployed successfully!"
    echo ""
    echo "🌐 Your cloud endpoints are now available at:"
    echo "   Non-compressed: https://us-central1-ecg-monitoring-system-bb817.cloudfunctions.net/processNonCompressed"
    echo "   Compressed: https://us-central1-ecg-monitoring-system-bb817.cloudfunctions.net/processCompressed"
    echo "   Health: https://us-central1-ecg-monitoring-system-bb817.cloudfunctions.net/health"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Update server.py with the cloud endpoints"
    echo "   2. Make sure your receiver is accessible from the internet"
    echo "   3. Test the cloud deployment"
    echo ""
    echo "🔒 Security Note: Make sure your receiver has proper security measures!"
else
    echo "❌ Deployment failed. Check the logs above."
    exit 1
fi

cd .. 