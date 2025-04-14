// src/components/StockDetail.jsx
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

function StockDetail() {
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { symbol } = useParams();

  useEffect(() => {
    setLoading(true);
    axios.get(`${API_BASE_URL}/stocks/${symbol}/detail/`)
      .then(response => {
        setStockData(response.data);
        setLoading(false);
      })
      .catch(error => {
        setError(`Error fetching data for ${symbol}: ${error.message}`);
        setLoading(false);
        console.error('Error fetching stock details:', error);
      });
  }, [symbol]);

  if (loading) return <div className="loading">Loading stock details...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!stockData) return <div>Stock not found</div>;

  return (
    <div className="stock-detail-container">
      <div className="header">
        <h1>{stockData.name} ({stockData.symbol})</h1>
        <Link to="/" className="back-link">Back to Indices</Link>
      </div>
      
      <div className="price-info">
        <div className="current-price">
          <h2>₺{stockData.current_price}</h2>
          <span className={stockData.current_price > stockData.previous_close ? "change positive" : "change negative"}>
            {((stockData.current_price - stockData.previous_close) / stockData.previous_close * 100).toFixed(2)}%
          </span>
        </div>
      </div>
      
      <div className="stock-grid">
        <div className="info-card">
          <h3>Market Summary</h3>
          <div className="info-row">
            <span>Previous Close</span>
            <span>₺{stockData.previous_close}</span>
          </div>
          <div className="info-row">
            <span>Open</span>
            <span>₺{stockData.open}</span>
          </div>
          <div className="info-row">
            <span>Day Range</span>
            <span>₺{stockData.day_low} - ₺{stockData.day_high}</span>
          </div>
          <div className="info-row">
            <span>Volume</span>
            <span>{stockData.volume.toLocaleString()}</span>
          </div>
          <div className="info-row">
            <span>Average Volume</span>
            <span>{stockData.average_volume.toLocaleString()}</span>
          </div>
        </div>

        <div className="info-card">
          <h3>Fundamentals</h3>
          <div className="info-row">
            <span>Market Cap</span>
            <span>₺{(stockData.market_cap / 1000000).toFixed(2)}M</span>
          </div>
          <div className="info-row">
            <span>P/E Ratio</span>
            <span>{stockData.PE_ratio.toFixed(2)}</span>
          </div>
          <div className="info-row">
            <span>EPS (TTM)</span>
            <span>₺{stockData.EPS}</span>
          </div>
          <div className="info-row">
            <span>Dividend Yield</span>
            <span>{(stockData.dividend_yield * 100).toFixed(2)}%</span>
          </div>
        </div>
      </div>
      
      <div className="historical-data">
        <h3>Historical Data (30 Days)</h3>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Open</th>
                <th>High</th>
                <th>Low</th>
                <th>Close</th>
                <th>Volume</th>
              </tr>
            </thead>
            <tbody>
              {stockData.historical_data.map((day, index) => (
                <tr key={index}>
                  <td>{day.date}</td>
                  <td>₺{day.open}</td>
                  <td>₺{day.high}</td>
                  <td>₺{day.low}</td>
                  <td>₺{day.close}</td>
                  <td>{day.volume.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default StockDetail;