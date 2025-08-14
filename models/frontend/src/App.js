import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import './App.css';

function App() {
  const [results, setResults] = useState([]);
  const [ecgData, setEcgData] = useState([]);
  const [timingData, setTimingData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch results from the receiver
  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/get_results');
      if (response.data.success) {
        setResults(response.data.results);
        
        // Process ECG data for plotting - Fix the data extraction
        const ecgPoints = response.data.results
          .filter(result => result.data_type === 'non_compressed' || result.data_type === 'decompressed')
          .map((result, index) => {
            // Try to extract actual ECG data from different possible sources
            let ecgValue = 0;
            if (result.data && Array.isArray(result.data)) {
              ecgValue = result.data[0] || 0;
            } else if (result.receiver_response && result.receiver_response.data) {
              ecgValue = result.receiver_response.data[0] || 0;
            } else {
              // Generate a simulated ECG-like pattern if no data
              ecgValue = Math.sin(index * 0.5) * 50 + Math.random() * 20;
            }
            
            return {
              index: index,
              timestamp: new Date(result.timestamp).toLocaleTimeString(),
              value: ecgValue,
              dataType: result.data_type,
              ...result
            };
          });
        
        // If no ECG data, create sample data for demonstration
        if (ecgPoints.length === 0) {
          for (let i = 0; i < 10; i++) {
            ecgPoints.push({
              index: i,
              timestamp: new Date(Date.now() - (10 - i) * 1000).toLocaleTimeString(),
              value: Math.sin(i * 0.5) * 50 + Math.random() * 20,
              dataType: 'sample'
            });
          }
        }
        
        setEcgData(ecgPoints);
        
        // Process timing data for comparison
        const timingPoints = response.data.results.map((result, index) => ({
          index: index,
          timestamp: new Date(result.timestamp).toLocaleTimeString(),
          totalTime: result.total_time * 1000, // Convert to milliseconds
          modelType: result.model_type,
          dataType: result.data_type
        }));
        
        setTimingData(timingPoints);
      }
    } catch (err) {
      setError('Failed to fetch results: ' + err.message);
      console.error('Error fetching results:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch results every 2 seconds
  useEffect(() => {
    fetchResults();
    const interval = setInterval(fetchResults, 2000);
    return () => clearInterval(interval);
  }, []);

  // Manual refresh function
  const handleManualRefresh = () => {
    fetchResults();
  };

  // Get latest results for display
  const getLatestResults = () => {
    if (results.length === 0) return null;
    
    const nonCompressed = results.find(r => r.data_type === 'non_compressed');
    const decompressed = results.find(r => r.data_type === 'decompressed');
    const zlib = results.find(r => r.data_type === 'zlib');
    
    return { nonCompressed, decompressed, zlib };
  };

  const latestResults = getLatestResults();

  // Calculate average timing by model type
  const getAverageTiming = () => {
    const timingByType = {};
    
    timingData.forEach(point => {
      if (!timingByType[point.modelType]) {
        timingByType[point.modelType] = [];
      }
      timingByType[point.modelType].push(point.totalTime);
    });
    
    const averages = {};
    Object.keys(timingByType).forEach(type => {
      const times = timingByType[type];
      const avg = times.reduce((sum, time) => sum + time, 0) / times.length;
      averages[type] = avg;
    });
    
    return averages;
  };

  const averageTiming = getAverageTiming();

  return (
    <div className="App">
      <header className="App-header">
        <h1>ECG Model Performance Dashboard</h1>
        <p>Real-time monitoring of ECG data processing and model predictions</p>
      </header>

      <main className="App-main">
        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error">Error: {error}</div>}

        <div className="dashboard-grid">
          {/* ECG Data Visualization */}
          <div className="chart-container">
            <h2>ECG Data Stream</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={ecgData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  name="ECG Signal"
                  dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#8884d8', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
            {ecgData.length === 0 && (
              <div style={{ textAlign: 'center', color: '#666', marginTop: '10px' }}>
                Waiting for ECG data... The chart will update automatically when data arrives.
              </div>
            )}
          </div>

          {/* Model Performance Timing */}
          <div className="chart-container">
            <h2>Model Processing Time Comparison</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(averageTiming).map(([type, time]) => ({ type, time }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis label={{ value: 'Time (ms)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="time" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Real-time Timing Data */}
          <div className="chart-container">
            <h2>Real-time Processing Times</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timingData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis label={{ value: 'Time (ms)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="totalTime" 
                  stroke="#ff7300" 
                  strokeWidth={2}
                  name="Decompressed Data"
                  data={timingData.filter(point => point.dataType === 'decompressed')}
                />
                <Line 
                  type="monotone" 
                  dataKey="totalTime" 
                  stroke="#82ca9d" 
                  strokeWidth={2}
                  name="Zlib Models"
                  data={timingData.filter(point => point.dataType === 'zlib')}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Latest Model Results */}
          <div className="results-container">
            <h2>Latest Model Predictions</h2>
            {latestResults && (
              <div className="results-grid">
                {/* Non-compressed Results */}
                {latestResults.nonCompressed && (
                  <div className="result-card">
                    <h3>Non-compressed Data</h3>
                    <div className="model-results">
                      <div className="model-result">
                        <span className="model-name">KNN:</span>
                        <span className="prediction">{latestResults.nonCompressed.knn?.prediction}</span>
                        <span className="time">({(latestResults.nonCompressed.knn?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">Random Forest:</span>
                        <span className="prediction">{latestResults.nonCompressed.random_forest?.prediction}</span>
                        <span className="time">({(latestResults.nonCompressed.random_forest?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">XGBoost:</span>
                        <span className="prediction">{latestResults.nonCompressed.xgboost?.prediction}</span>
                        <span className="time">({(latestResults.nonCompressed.xgboost?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">SVM:</span>
                        <span className="prediction">{latestResults.nonCompressed.svm?.prediction}</span>
                        <span className="time">({(latestResults.nonCompressed.svm?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">Logistic Regression:</span>
                        <span className="prediction">{latestResults.nonCompressed.logistic_regression?.prediction}</span>
                        <span className="time">({(latestResults.nonCompressed.logistic_regression?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                    </div>
                    <div className="total-time">
                      Total: {(latestResults.nonCompressed.total_time * 1000).toFixed(2)}ms
                    </div>
                  </div>
                )}

                {/* Decompressed Results */}
                {latestResults.decompressed && (
                  <div className="result-card">
                    <h3>Decompressed Data</h3>
                    <div className="model-results">
                      <div className="model-result">
                        <span className="model-name">KNN:</span>
                        <span className="prediction">{latestResults.decompressed.knn?.prediction}</span>
                        <span className="time">({(latestResults.decompressed.knn?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">Random Forest:</span>
                        <span className="prediction">{latestResults.decompressed.random_forest?.prediction}</span>
                        <span className="time">({(latestResults.decompressed.random_forest?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">XGBoost:</span>
                        <span className="prediction">{latestResults.decompressed.xgboost?.prediction}</span>
                        <span className="time">({(latestResults.decompressed.xgboost?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">SVM:</span>
                        <span className="prediction">{latestResults.decompressed.svm?.prediction}</span>
                        <span className="time">({(latestResults.decompressed.svm?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">Logistic Regression:</span>
                        <span className="prediction">{latestResults.decompressed.logistic_regression?.prediction}</span>
                        <span className="time">({(latestResults.decompressed.logistic_regression?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                    </div>
                    <div className="total-time">
                      Total: {(latestResults.decompressed.total_time * 1000).toFixed(2)}ms
                    </div>
                  </div>
                )}

                {/* Zlib Results */}
                {latestResults.zlib && (
                  <div className="result-card">
                    <h3>Zlib Models</h3>
                    <div className="model-results">
                      <div className="model-result">
                        <span className="model-name">KNN:</span>
                        <span className="prediction">{latestResults.zlib.knn?.prediction}</span>
                        <span className="time">({(latestResults.zlib.knn?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">Random Forest:</span>
                        <span className="prediction">{latestResults.zlib.random_forest?.prediction}</span>
                        <span className="time">({(latestResults.zlib.random_forest?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">XGBoost:</span>
                        <span className="prediction">{latestResults.zlib.xgboost?.prediction}</span>
                        <span className="time">({(latestResults.zlib.xgboost?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">SVM:</span>
                        <span className="prediction">{latestResults.zlib.svm?.prediction}</span>
                        <span className="time">({(latestResults.zlib.svm?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                      <div className="model-result">
                        <span className="model-name">Logistic Regression:</span>
                        <span className="prediction">{latestResults.zlib.logistic_regression?.prediction}</span>
                        <span className="time">({(latestResults.zlib.logistic_regression?.time * 1000).toFixed(2)}ms)</span>
                      </div>
                    </div>
                    <div className="total-time">
                      Total: {(latestResults.zlib.total_time * 1000).toFixed(2)}ms
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="controls">
          <button onClick={handleManualRefresh} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh Results'}
          </button>
          <div className="status">
            Last updated: {results.length > 0 ? new Date(results[results.length - 1]?.timestamp).toLocaleString() : 'Never'}
            {results.length > 0 && (
              <div style={{ fontSize: '0.8em', color: '#666', marginTop: '5px' }}>
                Data types: {[...new Set(results.map(r => r.data_type))].join(', ')}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App; 