import numpy as np
import pandas as pd
import zlib
import json
import time
import logging
import threading
import socket
import pickle
from datetime import datetime
import joblib
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class ModelReceiver:
    def __init__(self, port=None):
        """
        Initialize the model receiver
        
        Args:
            port: Port for the Flask server (defaults to config)
        """
        self.port = port or config.RECEIVER_PORT
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend communication
        
        # Load all models
        self.load_models()
        
        # Setup routes
        self.setup_routes()
        
        # Results storage
        self.results_buffer = []
        self.results_lock = threading.Lock()
    
    def load_models(self):
        """Load all trained models and scalers"""
        try:
            logger.info("Loading models and scalers...")
            
            # Non-compressed models
            self.knn_model = joblib.load('knn_model.joblib')
            self.random_forest_model = joblib.load('random_forest_model.joblib')
            self.xgboost_model = joblib.load('xgboost_model.joblib')
            self.svm_scaler = joblib.load('svm_scaler.joblib')
            self.svm_model = joblib.load('svm_model.joblib')
            self.logistic_scaler = joblib.load('logistic_regression_scaler.joblib')
            self.logistic_model = joblib.load('logistic_regression_model.joblib')
            
            # Zlib models
            self.knn_model_zlib = joblib.load('knn_model_zlib.joblib')
            self.random_forest_model_zlib = joblib.load('random_forest_model_zlib.joblib')
            self.xgboost_model_zlib = joblib.load('xgboost_model_zlib.joblib')
            self.svm_scaler_zlib = joblib.load('svm_scaler_zlib.joblib')
            self.svm_model_zlib = joblib.load('svm_model_zlib.joblib')
            self.logistic_scaler_zlib = joblib.load('logistic_regression_scaler_zlib.joblib')
            self.logistic_model_zlib = joblib.load('logistic_regression_model_zlib.joblib')
            
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def decompress_data(self, compressed_data_b64):
        """Decompress base64 encoded compressed data"""
        try:
            # Decode base64
            compressed_bytes = base64.b64decode(compressed_data_b64)
            # Decompress with zlib
            decompressed_bytes = zlib.decompress(compressed_bytes)
            # Convert back to numpy array
            decompressed_data = np.frombuffer(decompressed_bytes, dtype=np.float32)
            return decompressed_data
        except Exception as e:
            logger.error(f"Error decompressing data: {e}")
            raise
    
    def compress_data(self, data):
        """Compress data using the same method as training"""
        try:
            # Convert to numpy array if needed
            if isinstance(data, list):
                data = np.array(data, dtype=np.float32)
            
            # Reshape if needed
            if len(data.shape) == 1:
                data = data.reshape(1, -1)
            
            # Compress using the same logic as training
            byte_data = data.astype(np.float32).tobytes()
            compressed = zlib.compress(byte_data)
            
            # Convert to fixed-length array (like in training)
            compressed_array = np.frombuffer(compressed, dtype=np.uint8)
            
            # Pad to match training size (667 features)
            target_size = 667
            if len(compressed_array) < target_size:
                compressed_array = np.pad(compressed_array, (0, target_size - len(compressed_array)), constant_values=0)
            elif len(compressed_array) > target_size:
                compressed_array = compressed_array[:target_size]
            
            return compressed_array.reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error compressing data: {e}")
            raise
    
    def run_models_on_data(self, data, model_type="non_compressed"):
        """Run all models on the given data"""
        try:
            start_time = time.time()
            results = {}
            
            # Convert data to numpy array if it's a list
            if isinstance(data, list):
                data = np.array(data, dtype=np.float32)
            
            # Reshape data if needed (assuming single row)
            if len(data.shape) == 1:
                data = data.reshape(1, -1)
            
            logger.info(f"Running {model_type} models on data shape: {data.shape}")
            
            # Run KNN
            knn_start = time.time()
            if model_type == "zlib":
                knn_pred = self.knn_model_zlib.predict(data)[0]
            else:
                knn_pred = self.knn_model.predict(data)[0]
            knn_time = time.time() - knn_start
            results['knn'] = {'prediction': int(knn_pred), 'time': knn_time}
            
            # Run Random Forest
            rf_start = time.time()
            if model_type == "zlib":
                rf_pred = self.random_forest_model_zlib.predict(data)[0]
            else:
                rf_pred = self.random_forest_model.predict(data)[0]
            rf_time = time.time() - rf_start
            results['random_forest'] = {'prediction': int(rf_pred), 'time': rf_time}
            
            # Run XGBoost
            xgb_start = time.time()
            if model_type == "zlib":
                xgb_pred = self.xgboost_model_zlib.predict(data)[0]
            else:
                xgb_pred = self.xgboost_model.predict(data)[0]
            xgb_time = time.time() - xgb_start
            results['xgboost'] = {'prediction': int(xgb_pred), 'time': xgb_time}
            
            # Run SVM (with scaling)
            svm_start = time.time()
            if model_type == "zlib":
                data_scaled = self.svm_scaler_zlib.transform(data)
                svm_pred = self.svm_model_zlib.predict(data_scaled)[0]
            else:
                data_scaled = self.svm_scaler.transform(data)
                svm_pred = self.svm_model.predict(data_scaled)[0]
            svm_time = time.time() - svm_start
            results['svm'] = {'prediction': int(svm_pred), 'time': svm_time}
            
            # Run Logistic Regression (with scaling)
            lr_start = time.time()
            if model_type == "zlib":
                data_scaled = self.logistic_scaler_zlib.transform(data)
                lr_pred = self.logistic_model_zlib.predict(data_scaled)[0]
            else:
                data_scaled = self.logistic_scaler.transform(data)
                lr_pred = self.logistic_model.predict(data_scaled)[0]
            lr_time = time.time() - lr_start
            results['logistic_regression'] = {'prediction': int(lr_pred), 'time': lr_time}
            
            total_time = time.time() - start_time
            results['total_time'] = total_time
            results['model_type'] = model_type
            
            logger.info(f"{model_type} models completed in {total_time:.4f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Error running {model_type} models: {e}")
            raise
    
    def process_non_compressed_data(self, data_payload):
        """Process non-compressed data through all models"""
        try:
            timestamp = data_payload.get('timestamp')
            data = data_payload.get('data')
            
            logger.info(f"Processing non-compressed data with timestamp: {timestamp}")
            
            # Run models on non-compressed data
            results = self.run_models_on_data(data, "non_compressed")
            results['timestamp'] = timestamp
            results['data_type'] = 'non_compressed'
            
            # Store results
            with self.results_lock:
                self.results_buffer.append(results)
                # Keep only last 100 results
                if len(self.results_buffer) > 100:
                    self.results_buffer.pop(0)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing non-compressed data: {e}")
            raise
    
    def process_compressed_data(self, compressed_payload):
        """Process compressed data through all models"""
        try:
            timestamp = compressed_payload.get('timestamp')
            compressed_data_b64 = compressed_payload.get('compressed_data')
            
            logger.info(f"Processing compressed data with timestamp: {timestamp}")
            logger.info(f"Compressed data size: {compressed_payload.get('compressed_size', 'N/A')}")
            logger.info(f"Compression type: {compressed_payload.get('compression_type', 'N/A')}")
            
            # Decompress data
            decompressed_data = self.decompress_data(compressed_data_b64)
            logger.info(f"Decompressed data shape: {decompressed_data.shape if hasattr(decompressed_data, 'shape') else 'N/A'}")
            
            # Run models on decompressed data (standard models)
            results = self.run_models_on_data(decompressed_data, "decompressed")
            results['timestamp'] = timestamp
            results['data_type'] = 'decompressed'
            
            # Compress data for zlib models (matching training process)
            compressed_for_zlib = self.compress_data(decompressed_data)
            logger.info(f"Compressed data for zlib models shape: {compressed_for_zlib.shape}")
            
            # Run models on compressed data (zlib models)
            zlib_results = self.run_models_on_data(compressed_for_zlib, "zlib")
            zlib_results['timestamp'] = timestamp
            zlib_results['data_type'] = 'zlib'
            
            # Store both results
            with self.results_lock:
                self.results_buffer.append(results)
                self.results_buffer.append(zlib_results)
                # Keep only last 100 results
                if len(self.results_buffer) > 100:
                    self.results_buffer.pop(0)
                    self.results_buffer.pop(0)
            
            logger.info(f"Successfully processed compressed data - stored {len(results)} and {len(zlib_results)} results")
            
            return {
                'decompressed_results': results,
                'zlib_results': zlib_results
            }
            
        except Exception as e:
            logger.error(f"Error processing compressed data: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/process_non_compressed', methods=['POST'])
        def handle_non_compressed():
            try:
                data = request.json
                results = self.process_non_compressed_data(data)
                return jsonify({'success': True, 'results': results})
            except Exception as e:
                logger.error(f"Error handling non-compressed data: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/process_compressed', methods=['POST'])
        def handle_compressed():
            try:
                data = request.json
                results = self.process_compressed_data(data)
                return jsonify({'success': True, 'results': results})
            except Exception as e:
                logger.error(f"Error handling compressed data: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/get_results', methods=['GET'])
        def get_results():
            """Get all stored results for frontend"""
            try:
                with self.results_lock:
                    return jsonify({
                        'success': True,
                        'results': self.results_buffer,
                        'count': len(self.results_buffer)
                    })
            except Exception as e:
                logger.error(f"Error getting results: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
    
    def run(self):
        """Run the Flask server"""
        logger.info(f"Starting Model Receiver on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

if __name__ == "__main__":
    # Print current configuration
    config.print_config()
    
    # Create and run receiver
    receiver = ModelReceiver()
    receiver.run() 