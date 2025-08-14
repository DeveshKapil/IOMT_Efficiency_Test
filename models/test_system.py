#!/usr/bin/env python3
"""
Test script for the ECG Model System with Firebase Functions
This script tests the basic functionality of all components
"""

import requests
import json
import time
import numpy as np
import zlib
import base64
from datetime import datetime

def test_firebase_health():
    """Test if Firebase Functions are running and healthy"""
    try:
        response = requests.get('http://localhost:5002/ecg-monitoring-system-bb817/us-central1/health', timeout=5)
        if response.status_code == 200:
            print("✅ Firebase Functions health check passed")
            return True
        else:
            print(f"❌ Firebase Functions health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Firebase Functions health check failed: {e}")
        return False

def test_firebase_test_endpoint():
    """Test the Firebase Functions test endpoint"""
    try:
        response = requests.get('http://localhost:5002/ecg-monitoring-system-bb817/us-central1/test', timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Firebase Functions test endpoint passed")
            print(f"   Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Firebase Functions test endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Firebase Functions test endpoint failed: {e}")
        return False

def test_non_compressed_processing():
    """Test processing of non-compressed data through Firebase Functions"""
    try:
        # Create sample ECG data (simulating one row with 187 features)
        sample_data = np.random.randn(187).astype(np.float32).tolist()
        
        payload = {
            "timestamp": datetime.now().isoformat(),
            "data": sample_data,
            "data_shape": [1, 187],
            "data_type": "float32"
        }
        
        response = requests.post(
            'http://localhost:5002/ecg-monitoring-system-bb817/us-central1/processNonCompressed',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Non-compressed data processing through Firebase passed")
                return True
            else:
                print(f"❌ Non-compressed processing failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Non-compressed processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Non-compressed processing test failed: {e}")
        return False

def test_compressed_processing():
    """Test processing of compressed data through Firebase Functions"""
    try:
        # Create sample ECG data (187 features) and compress it
        sample_data = np.random.randn(187).astype(np.float32)
        byte_data = sample_data.tobytes()
        compressed = zlib.compress(byte_data)
        compressed_b64 = base64.b64encode(compressed).decode('utf-8')
        
        payload = {
            "timestamp": datetime.now().isoformat(),
            "compressed_data": compressed_b64,
            "compressed_size": len(compressed),
            "compression_type": "zlib"
        }
        
        response = requests.post(
            'http://localhost:5002/ecg-monitoring-system-bb817/us-central1/processCompressed',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Compressed data processing through Firebase passed")
                return True
            else:
                print(f"❌ Compressed processing failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Compressed processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Compressed processing test failed: {e}")
        return False

def test_receiver_health():
    """Test if the receiver is running and healthy"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Receiver health check passed")
            return True
        else:
            print(f"❌ Receiver health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Receiver health check failed: {e}")
        return False

def test_results_retrieval():
    """Test retrieving results from the receiver"""
    try:
        response = requests.get('http://localhost:5000/get_results', timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                count = result.get('count', 0)
                print(f"✅ Results retrieval test passed. Found {count} results")
                return True
            else:
                print(f"❌ Results retrieval failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Results retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Results retrieval test failed: {e}")
        return False

def test_frontend_connection():
    """Test if frontend can connect to the receiver"""
    try:
        # Test if frontend proxy is working
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend connection test passed")
            return True
        else:
            print(f"❌ Frontend connection failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend connection test failed: {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("🚀 Starting ECG Model System Tests with Firebase Functions...")
    print("=" * 60)
    
    tests = [
        ("Firebase Functions Test Endpoint", test_firebase_test_endpoint),
        ("Firebase Functions Health Check", test_firebase_health),
        ("Non-compressed Data Processing (Firebase)", test_non_compressed_processing),
        ("Compressed Data Processing (Firebase)", test_compressed_processing),
        ("Receiver Health Check", test_receiver_health),
        ("Results Retrieval", test_results_retrieval),
        ("Frontend Connection", test_frontend_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    print("ECG Model System Test Suite (Firebase Functions)")
    print("Make sure all services are running before executing tests.")
    print("Run './start_system_firebase.sh' first if you haven't already.")
    print()
    
    input("Press Enter to continue with tests...")
    
    success = run_all_tests()
    
    if success:
        print("\n🎯 System is ready for use!")
        print("Open http://localhost:3000 in your browser to view the dashboard.")
        print("Firebase Functions are running on http://localhost:5002")
    else:
        print("\n🔧 Please fix the failing tests before using the system.") 