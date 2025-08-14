import pandas as pd
import numpy as np
import zlib
import json
import time
import requests
import random
from datetime import datetime
import logging
from config import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class DataServer:
    def __init__(self, csv_file_path, firebase_endpoint_1, firebase_endpoint_2):
        """
        Initialize the data server
        
        Args:
            csv_file_path: Path to the CSV file containing ECG data
            firebase_endpoint_1: Firebase Function endpoint for non-compressed data
            firebase_endpoint_2: Firebase Function endpoint for compressed data
        """
        self.csv_file_path = csv_file_path
        self.firebase_endpoint_1 = firebase_endpoint_1
        self.firebase_endpoint_2 = firebase_endpoint_2
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load CSV data into memory"""
        try:
            self.data = pd.read_csv(self.csv_file_path)
            logger.info(f"Loaded {len(self.data)} rows from {self.csv_file_path}")
        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            raise
    
    def select_random_row(self):
        """Select a random row from the dataset"""
        if self.data is None or len(self.data) == 0:
            raise ValueError("No data loaded")
        
        random_index = random.randint(0, len(self.data) - 1)
        selected_row = self.data.iloc[random_index]
        return selected_row
    
    def compress_data(self, data_row):
        """Compress a single row using zlib"""
        try:
            # Convert pandas Series to numpy array first, then to bytes
            if hasattr(data_row, 'values'):
                # Handle pandas Series
                data_array = data_row.values.astype(np.float32)
            else:
                # Handle numpy array or other types
                data_array = np.array(data_row, dtype=np.float32)
            
            byte_data = data_array.tobytes()
            compressed = zlib.compress(byte_data)
            return compressed
        except Exception as e:
            logger.error(f"Error compressing data: {e}")
            raise
    
    def create_timestamp(self):
        """Create current timestamp"""
        return datetime.now().isoformat()
    
    def prepare_data_payload(self, data_row, timestamp):
        """Prepare data payload with timestamp"""
        # Convert pandas Series to list for JSON serialization
        if hasattr(data_row, 'values'):
            # Handle pandas Series
            data_list = data_row.values.tolist()
        else:
            # Handle numpy array or other types
            data_list = data_row.tolist() if hasattr(data_row, 'tolist') else list(data_row)
        
        payload = {
            "timestamp": timestamp,
            "data": data_list,
            "data_shape": data_row.shape if hasattr(data_row, 'shape') else [1, len(data_list)],
            "data_type": str(data_row.dtype) if hasattr(data_row, 'dtype') else 'float32'
        }
        return payload
    
    def prepare_compressed_payload(self, compressed_data, timestamp):
        """Prepare compressed data payload with timestamp"""
        # Convert compressed bytes to base64 for JSON transmission
        import base64
        compressed_b64 = base64.b64encode(compressed_data).decode('utf-8')
        
        payload = {
            "timestamp": timestamp,
            "compressed_data": compressed_b64,
            "compressed_size": len(compressed_data),
            "compression_type": "zlib"
        }
        return payload
    
    def send_to_firebase(self, endpoint, payload):
        """Send data to Firebase Function endpoint"""
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully sent data to {endpoint}")
                return True
            else:
                logger.error(f"Failed to send data to {endpoint}. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending data to {endpoint}: {e}")
            return False
    
    def process_and_send_data(self):
        """Main method to process and send data"""
        try:
            # Select random row
            selected_row = self.select_random_row()
            timestamp = self.create_timestamp()
            
            logger.info(f"Selected row at index {selected_row.name}, timestamp: {timestamp}")
            logger.info(f"Data type: {type(selected_row)}, Shape: {getattr(selected_row, 'shape', 'N/A')}")
            
            # Prepare non-compressed payload
            non_compressed_payload = self.prepare_data_payload(selected_row, timestamp)
            
            # Prepare compressed payload
            compressed_data = self.compress_data(selected_row)
            compressed_payload = self.prepare_compressed_payload(compressed_data, timestamp)
            
            # Send non-compressed data to first Firebase endpoint
            success1 = self.send_to_firebase(self.firebase_endpoint_1, non_compressed_payload)
            
            # Send compressed data to second Firebase endpoint
            success2 = self.send_to_firebase(self.firebase_endpoint_2, compressed_payload)
            
            if success1 and success2:
                logger.info("Successfully sent both data streams")
                return True
            else:
                logger.warning("Some data streams failed to send")
                return False
                
        except Exception as e:
            logger.error(f"Error in process_and_send_data: {e}")
            return False
    
    def run_continuous(self, interval_seconds=5):
        """Run the server continuously, sending data at specified intervals"""
        logger.info(f"Starting continuous data transmission every {interval_seconds} seconds")
        
        try:
            while True:
                self.process_and_send_data()
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")

if __name__ == "__main__":
    # Print current configuration
    config.print_config()
    
    # Create and run server using centralized configuration
    server = DataServer(
        csv_file_path=config.CSV_FILE_PATH,
        firebase_endpoint_1=config.firebase_endpoint_1,
        firebase_endpoint_2=config.firebase_endpoint_2
    )
    
    # Run continuously
    server.run_continuous(interval_seconds=config.DATA_INTERVAL_SECONDS) 