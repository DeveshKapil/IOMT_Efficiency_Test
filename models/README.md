# ECG Model Performance Dashboard

A comprehensive system for real-time ECG data processing and model performance monitoring using multiple machine learning models with compression/decompression capabilities.

## System Architecture

The system consists of three main components:

1. **Data Server** (`server.py`) - Reads CSV data, selects random rows, compresses data using zlib, and sends to AWS Lambda endpoints
2. **Model Receiver** (`receiver.py`) - Flask server that runs all ML models independently and processes both compressed and non-compressed data
3. **React Frontend** (`frontend/`) - Real-time dashboard showing ECG data, model predictions, and performance metrics

## Features

- **Real-time Data Processing**: Continuous data stream from CSV with random row selection
- **Dual Data Paths**: 
  - Non-compressed data → Standard models
  - Compressed data → Decompressed → Standard models + Zlib-specific models
- **Multiple ML Models**: KNN, Random Forest, XGBoost, SVM, Logistic Regression
- **Performance Monitoring**: Real-time timing comparisons and visualizations
- **Modern UI**: Responsive React dashboard with interactive charts

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Your ECG CSV data file
- AWS Lambda endpoints (for production use)

## Installation

### 1. Clone and Setup

```bash
# Make the startup script executable
chmod +x start_system.sh

# Install Python dependencies
pip3 install -r requirements.txt
```

### 2. Configure Your Data

Update the configuration in `server.py`:

```python
CSV_FILE_PATH = "path/to/your/ecg_data.csv"  # Update this path
LAMBDA_ENDPOINT_1 = "https://your-lambda-1-url.amazonaws.com/process"  # Update this URL
LAMBDA_ENDPOINT_2 = "https://your-lambda-2-url.amazonaws.com/process"  # Update this URL
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Usage

### Quick Start

Use the provided startup script to launch all components:

```bash
./start_system.sh
```

This will:
- Start the Model Receiver on port 5000
- Start the React Frontend on port 3000
- Open your browser to the dashboard

### Manual Start

#### 1. Start Model Receiver

```bash
python3 receiver.py
```

The receiver will load all models and start listening on port 5000.

#### 2. Start Frontend

```bash
cd frontend
npm start
```

The frontend will open in your browser at http://localhost:3000.

#### 3. Start Data Server (Optional)

```bash
python3 server.py
```

This will start sending data to your configured Lambda endpoints.

## API Endpoints

### Model Receiver (Port 5000)

- `POST /process_non_compressed` - Process non-compressed data
- `POST /process_compressed` - Process compressed data
- `GET /get_results` - Get all stored results
- `GET /health` - Health check

### Data Server

The server sends data to two Lambda endpoints:
- **Endpoint 1**: Non-compressed data
- **Endpoint 2**: Compressed data (zlib)

## Data Flow

```
CSV Data → Random Row Selection → Timestamp Addition
                ↓
    ┌─────────────────┬─────────────────┐
    │                 │                 │
Non-compressed    Compressed      Compressed
    │                 │                 │
    ↓                 ↓                 ↓
Lambda 1         Lambda 2         Lambda 2
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

## Model Types

### Standard Models
- KNN
- Random Forest  
- XGBoost
- SVM (with scaling)
- Logistic Regression (with scaling)

### Zlib Models
- KNN (trained on compressed data)
- Random Forest (trained on compressed data)
- XGBoost (trained on compressed data)
- SVM (trained on compressed data)
- Logistic Regression (trained on compressed data)

## Dashboard Features

### Real-time Charts
1. **ECG Data Stream** - Live ECG data visualization
2. **Model Performance Timing** - Bar chart comparing average processing times
3. **Real-time Processing Times** - Line chart showing timing trends

### Model Results Display
- Individual model predictions
- Processing time per model
- Total processing time per data type
- Comparison between compressed/non-compressed performance

## Configuration

### Server Configuration

Edit `server.py` to configure:
- CSV file path
- Lambda endpoints
- Data transmission interval
- Logging level

### Receiver Configuration

Edit `receiver.py` to configure:
- Port number
- Model loading paths
- Results buffer size
- Logging level

### Frontend Configuration

Edit `frontend/src/App.js` to configure:
- Data refresh interval
- Chart configurations
- API endpoints

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill processes on specific ports
   lsof -ti:5000 | xargs kill -9
   lsof -ti:3000 | xargs kill -9
   ```

2. **Model Loading Errors**
   - Ensure all `.joblib` files are in the project root
   - Check file permissions
   - Verify model compatibility

3. **Frontend Connection Issues**
   - Check if receiver is running on port 5000
   - Verify CORS settings
   - Check browser console for errors

### Logs

- **Server**: Check terminal output for data transmission logs
- **Receiver**: Check terminal output for model processing logs
- **Frontend**: Check browser console for API errors

## Performance Optimization

### For High-Volume Data
- Increase data transmission interval in server
- Implement data batching
- Use Redis for results caching
- Implement model result aggregation

### For Real-time Requirements
- Decrease data transmission interval
- Implement WebSocket connections
- Use streaming responses
- Optimize model inference

## Security Considerations

- Implement authentication for API endpoints
- Use HTTPS in production
- Validate input data
- Implement rate limiting
- Secure AWS Lambda endpoints

## Production Deployment

### Docker Support
```bash
# Build and run with Docker
docker build -t ecg-dashboard .
docker run -p 5000:5000 -p 3000:3000 ecg-dashboard
```

### Environment Variables
```bash
export CSV_FILE_PATH="/path/to/ecg_data.csv"
export LAMBDA_ENDPOINT_1="https://your-lambda-1.amazonaws.com"
export LAMBDA_ENDPOINT_2="https://your-lambda-2.amazonaws.com"
export FLASK_ENV="production"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs and error messages
3. Open an issue on GitHub
4. Contact the development team

## Changelog

### Version 1.0.0
- Initial release
- Basic server, receiver, and frontend
- Support for all model types
- Real-time dashboard
- Compression/decompression capabilities 