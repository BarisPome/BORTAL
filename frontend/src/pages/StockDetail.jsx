// src/pages/StockDetail.jsx
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getStockDetail } from '../services/stockService';
import { formatCurrency, formatNumber, formatPercentage } from '../utils/formatters';
import '../styles/components/stock-detail.css';

function StockDetail() {
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { symbol } = useParams();

  useEffect(() => {
    const fetchStockDetail = async () => {
      try {
        console.log("Fetching stock data for:", symbol);
        const data = await getStockDetail(symbol);
        console.log("Received stock data:", data);
        setStockData(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching stock details:", error);
        setError(`Error fetching data for ${symbol}: ${error.message}`);
        setLoading(false);
      }
    };

    fetchStockDetail();
  }, [symbol]);

  if (loading) return <div className="loading">Loading stock details...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!stockData) return <div>Stock not found</div>;

  const priceChange = stockData.current_price - stockData.previous_close;
  const priceChangePercent = (priceChange / stockData.previous_close) * 100;

  return (
    <div className="stock-detail-container">
      <div className="header">
        <h1>{stockData.name} ({stockData.symbol})</h1>
        <Link to="/" className="back-link">Back to Indices</Link>
      </div>
      
      <div className="price-info">
        <div className="current-price">
          <h2>{formatCurrency(stockData.current_price)}</h2>
          <span className={priceChange >= 0 ? "change positive" : "change negative"}>
            {priceChange >= 0 ? "+" : ""}{formatPercentage(priceChangePercent)}
          </span>
        </div>
      </div>
      
      <div className="stock-grid">
        <div className="info-card">
          <h3>Market Summary</h3>
          <div className="info-row">
            <span>Previous Close</span>
            <span>{formatCurrency(stockData.previous_close)}</span>
          </div>
          <div className="info-row">
            <span>Open</span>
            <span>{formatCurrency(stockData.open)}</span>
          </div>
          <div className="info-row">
            <span>Day Range</span>
            <span>{formatCurrency(stockData.day_low)} - {formatCurrency(stockData.day_high)}</span>
          </div>
          <div className="info-row">
            <span>Volume</span>
            <span>{formatNumber(stockData.volume)}</span>
          </div>
          <div className="info-row">
            <span>Average Volume</span>
            <span>{formatNumber(stockData.average_volume)}</span>
          </div>
        </div>

        <div className="info-card">
          <h3>Fundamentals</h3>
          <div className="info-row">
            <span>Market Cap</span>
            <span>{formatCurrency(stockData.market_cap / 1000000)}M</span>
          </div>
          <div className="info-row">
            <span>P/E Ratio</span>
            <span>{stockData.PE_ratio.toFixed(2)}</span>
          </div>
          <div className="info-row">
            <span>EPS (TTM)</span>
            <span>{formatCurrency(stockData.EPS)}</span>
          </div>
          <div className="info-row">
            <span>Dividend Yield</span>
            <span>{formatPercentage(stockData.dividend_yield * 100)}</span>
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
                  <td>{formatCurrency(day.open)}</td>
                  <td>{formatCurrency(day.high)}</td>
                  <td>{formatCurrency(day.low)}</td>
                  <td>{formatCurrency(day.close)}</td>
                  <td>{formatNumber(day.volume)}</td>
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