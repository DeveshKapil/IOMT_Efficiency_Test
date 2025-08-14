import socket
import os
import requests
from typing import Optional

class Config:
    """Centralized configuration for the ECG Model System"""
    
    def __init__(self):
        self._local_ip = None
        self._public_ip = None
        self._ngrok_url = None
        
    @property
    def local_ip(self) -> str:
        """Get local IP address"""
        if self._local_ip is None:
            try:
                # Get local IP by connecting to a remote address
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    self._local_ip = s.getsockname()[0]
            except Exception:
                self._local_ip = "127.0.0.1"
        return self._local_ip
    
    @property
    def public_ip(self) -> str:
        """Get public IP address"""
        if self._public_ip is None:
            try:
                response = requests.get("https://api.ipify.org", timeout=5)
                self._public_ip = response.text
            except Exception:
                self._public_ip = self.local_ip
        return self._public_ip
    
    @property
    def ngrok_url(self) -> Optional[str]:
        """Get ngrok URL if available"""
        if self._ngrok_url is None:
            try:
                response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
                data = response.json()
                if data.get("tunnels"):
                    self._ngrok_url = data["tunnels"][0]["public_url"]
            except Exception:
                self._ngrok_url = None
        return self._ngrok_url
    
    # Ports
    RECEIVER_PORT = 5000
    FRONTEND_PORT = 3000
    FIREBASE_EMULATOR_PORT = 5002
    FIREBASE_UI_PORT = 4001
    NGROK_API_PORT = 4040
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID = "ecg-monitoring-system-bb817"
    FIREBASE_REGION = "us-central1"
    
    # URLs
    @property
    def receiver_url(self) -> str:
        """Get receiver URL (prefer ngrok, fallback to local)"""
        if self.ngrok_url:
            return f"{self.ngrok_url}"
        return f"http://{self.local_ip}:{self.RECEIVER_PORT}"
    
    @property
    def receiver_local_url(self) -> str:
        """Get local receiver URL"""
        return f"http://localhost:{self.RECEIVER_PORT}"
    
    @property
    def frontend_url(self) -> str:
        """Get frontend URL"""
        return f"http://localhost:{self.FRONTEND_PORT}"
    
    @property
    def firebase_emulator_url(self) -> str:
        """Get Firebase emulator URL"""
        return f"http://localhost:{self.FIREBASE_EMULATOR_PORT}"
    
    @property
    def firebase_cloud_url(self) -> str:
        """Get Firebase cloud URL"""
        return f"https://{self.FIREBASE_REGION}-{self.FIREBASE_PROJECT_ID}.cloudfunctions.net"
    
    # Endpoints
    @property
    def firebase_endpoint_1(self) -> str:
        """Get Firebase non-compressed endpoint"""
        return f"{self.firebase_cloud_url}/processNonCompressed"
    
    @property
    def firebase_endpoint_2(self) -> str:
        """Get Firebase compressed endpoint"""
        return f"{self.firebase_cloud_url}/processCompressed"
    
    @property
    def firebase_health_endpoint(self) -> str:
        """Get Firebase health endpoint"""
        return f"{self.firebase_cloud_url}/health"
    
    @property
    def firebase_test_endpoint(self) -> str:
        """Get Firebase test endpoint"""
        return f"{self.firebase_cloud_url}/test"
    
    # Receiver endpoints
    @property
    def receiver_health_endpoint(self) -> str:
        """Get receiver health endpoint"""
        return f"{self.receiver_local_url}/health"
    
    @property
    def receiver_results_endpoint(self) -> str:
        """Get receiver results endpoint"""
        return f"{self.receiver_local_url}/get_results"
    
    # Data transmission settings
    DATA_INTERVAL_SECONDS = 1
    CSV_FILE_PATH = "exported_data.csv"
    
    # Model settings
    COMPRESSED_FEATURES = 667
    STANDARD_FEATURES = 187
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    
    def print_config(self):
        """Print current configuration"""
        print("=" * 60)
        print("🔧 ECG Model System Configuration")
        print("=" * 60)
        print(f"🌐 Local IP: {self.local_ip}")
        print(f"🌍 Public IP: {self.public_ip}")
        print(f"🔗 Ngrok URL: {self.ngrok_url or 'Not available'}")
        print()
        print("📡 URLs:")
        print(f"   Receiver (Local): {self.receiver_local_url}")
        print(f"   Receiver (Public): {self.receiver_url}")
        print(f"   Frontend: {self.frontend_url}")
        print(f"   Firebase (Cloud): {self.firebase_cloud_url}")
        print(f"   Firebase (Emulator): {self.firebase_emulator_url}")
        print()
        print("🔌 Ports:")
        print(f"   Receiver: {self.RECEIVER_PORT}")
        print(f"   Frontend: {self.FRONTEND_PORT}")
        print(f"   Firebase Emulator: {self.FIREBASE_EMULATOR_PORT}")
        print(f"   Firebase UI: {self.FIREBASE_UI_PORT}")
        print(f"   Ngrok API: {self.NGROK_API_PORT}")
        print()
        print("🎯 Endpoints:")
        print(f"   Firebase Health: {self.firebase_health_endpoint}")
        print(f"   Firebase Test: {self.firebase_test_endpoint}")
        print(f"   Receiver Health: {self.receiver_health_endpoint}")
        print(f"   Receiver Results: {self.receiver_results_endpoint}")
        print("=" * 60)

# Global configuration instance
config = Config()

if __name__ == "__main__":
    config.print_config()
