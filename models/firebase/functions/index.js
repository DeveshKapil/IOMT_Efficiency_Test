const functions = require('firebase-functions');
const admin = require('firebase-admin');
const axios = require('axios');
const cors = require('cors')({ origin: true });
const FirebaseConfig = require('./config');

// Load environment variables
require('dotenv').config();

// Initialize Firebase Admin
admin.initializeApp();

// Initialize configuration
const config = new FirebaseConfig();

// Log the configuration
console.log('Firebase Functions initialized with configuration');
console.log('Log level:', FirebaseConfig.LOG_LEVEL);
console.log('Timeout:', FirebaseConfig.TIMEOUT);

/**
 * Firebase Function to process non-compressed ECG data
 * Receives data from the server and forwards it to the receiver
 */
exports.processNonCompressed = functions.https.onRequest((request, response) => {
  cors(request, response, async () => {
    try {
      // Log the incoming request
      console.log('Received non-compressed data request:', {
        timestamp: request.body.timestamp,
        dataShape: request.body.data_shape,
        dataType: request.body.data_type
      });

      // Validate request
      if (!request.body.data || !request.body.timestamp) {
        console.error('Invalid request: missing required fields');
        return response.status(400).json({
          success: false,
          error: 'Missing required fields: data and timestamp'
        });
      }

      // Get receiver URL dynamically
      const receiverUrl = await config.getReceiverUrl();
      
      // Forward data to your receiver
      const receiverResponse = await axios.post(
        `${receiverUrl}/process_non_compressed`,
        request.body,
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: FirebaseConfig.TIMEOUT
        }
      );

      console.log('Successfully forwarded non-compressed data to receiver');

      // Return success response
      response.status(200).json({
        success: true,
        message: 'Non-compressed data processed successfully',
        timestamp: request.body.timestamp,
        data_type: 'non_compressed',
        receiver_response: receiverResponse.data
      });

    } catch (error) {
      console.error('Error processing non-compressed data:', error.message);
      
      // Check if it's a receiver connection error
      if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
        return response.status(503).json({
          success: false,
          error: 'Receiver service unavailable',
          details: 'Cannot connect to the model receiver'
        });
      }

      // Check if it's a timeout error
      if (error.code === 'ECONNABORTED') {
        return response.status(504).json({
          success: false,
          error: 'Request timeout',
          details: 'Receiver took too long to respond'
        });
      }

      // Generic error response
      response.status(500).json({
        success: false,
        error: 'Internal server error',
        details: error.message
      });
    }
  });
});

/**
 * Firebase Function to process compressed ECG data
 * Receives compressed data from the server and forwards it to the receiver
 */
exports.processCompressed = functions.https.onRequest((request, response) => {
  cors(request, response, async () => {
    try {
      // Log the incoming request
      console.log('Received compressed data request:', {
        timestamp: request.body.timestamp,
        compressedSize: request.body.compressed_size,
        compressionType: request.body.compression_type
      });

      // Validate request
      if (!request.body.compressed_data || !request.body.timestamp) {
        console.error('Invalid request: missing required fields');
        return response.status(400).json({
          success: false,
          error: 'Missing required fields: compressed_data and timestamp'
        });
      }

      // Get receiver URL dynamically
      const receiverUrl = await config.getReceiverUrl();
      
      // Forward compressed data to your receiver
      const receiverResponse = await axios.post(
        `${receiverUrl}/process_compressed`,
        request.body,
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: FirebaseConfig.TIMEOUT
        }
      );

      console.log('Successfully forwarded compressed data to receiver');

      // Return success response
      response.status(200).json({
        success: true,
        message: 'Compressed data processed successfully',
        timestamp: request.body.timestamp,
        data_type: 'compressed',
        receiver_response: receiverResponse.data
      });

    } catch (error) {
      console.error('Error processing compressed data:', error.message);
      
      // Check if it's a receiver connection error
      if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
        return response.status(503).json({
          success: false,
          error: 'Receiver service unavailable',
          details: 'Cannot connect to the model receiver'
        });
      }

      // Check if it's a timeout error
      if (error.code === 'ECONNABORTED') {
        return response.status(504).json({
          success: false,
          error: 'Request timeout',
          details: 'Receiver took too long to respond'
        });
      }

      // Generic error response
      response.status(500).json({
        success: false,
        error: 'Internal server error',
        details: error.message
      });
    }
  });
});

/**
 * Health check endpoint
 */
exports.health = functions.https.onRequest((request, response) => {
  cors(request, response, async () => {
    try {
      // Get receiver URL dynamically
      const receiverUrl = await config.getReceiverUrl();
      
      // Test connection to receiver
      const receiverResponse = await axios.get(`${receiverUrl}/health`, {
        timeout: 5000
      });

      response.status(200).json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        receiver_status: 'connected',
        receiver_response: receiverResponse.data
      });

    } catch (error) {
      console.error('Health check failed:', error.message);
      
      response.status(503).json({
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        receiver_status: 'disconnected',
        error: error.message
      });
    }
  });
});

/**
 * Test endpoint for development
 */
exports.test = functions.https.onRequest((request, response) => {
  cors(request, response, () => {
    response.status(200).json({
      message: 'Firebase Functions are working!',
      timestamp: new Date().toISOString(),
      endpoints: {
        non_compressed: '/processNonCompressed',
        compressed: '/processCompressed',
        health: '/health'
      }
    });
  });
}); 