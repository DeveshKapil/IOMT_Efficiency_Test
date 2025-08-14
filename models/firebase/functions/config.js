// Firebase Functions Configuration
const axios = require('axios');

class FirebaseConfig {
    constructor() {
        this._receiverUrl = null;
    }

    async getReceiverUrl() {
        if (this._receiverUrl) {
            return this._receiverUrl;
        }

        // First try environment variable
        if (process.env.RECEIVER_URL) {
            this._receiverUrl = process.env.RECEIVER_URL;
            console.log('Using receiver URL from environment:', this._receiverUrl);
            return this._receiverUrl;
        }

        // Try to get ngrok URL automatically
        try {
            const response = await axios.get('http://localhost:4040/api/tunnels', { timeout: 2000 });
            const tunnels = response.data.tunnels;
            if (tunnels && tunnels.length > 0) {
                this._receiverUrl = tunnels[0].public_url;
                console.log('Auto-detected ngrok URL:', this._receiverUrl);
                return this._receiverUrl;
            }
        } catch (error) {
            console.log('Could not auto-detect ngrok URL:', error.message);
        }

        // Fallback to hardcoded URL
        this._receiverUrl = 'http://106.222.138.233:5000';
        console.log('Using fallback receiver URL:', this._receiverUrl);
        return this._receiverUrl;
    }

    // Configuration constants
    static get TIMEOUT() {
        return 30000; // 30 seconds
    }

    static get CORS_ORIGINS() {
        return ['*']; // Allow all origins
    }

    static get LOG_LEVEL() {
        return process.env.LOG_LEVEL || 'info';
    }
}

module.exports = FirebaseConfig;
