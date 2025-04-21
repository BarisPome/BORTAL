import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getStockDetail } from '../services/stockService';
import { formatCurrency, formatNumber, formatPercentage } from '../utils/formatters';
import '../styles/components/stock-detail.css';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Area,
  AreaChart
} from 'recharts';

function StockDetail() {
  const { symbol } = useParams();
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [range, setRange] = useState('1m'); // default: 1 month
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchStockDetail = async () => {
      try {
        const response = await getStockDetail(symbol, range);
        setStockData(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching stock details:", error);
        setError(`Error fetching data for ${symbol}: ${error.message}`);
        setLoading(false);
      }
    };

    fetchStockDetail();
  }, [symbol, range]);

  if (loading) return <div className="loading-container"><div className="loading-spinner"></div><div>Loading stock details...</div></div>;
  if (error) return <div className="error-container"><div className="error-icon">⚠️</div><div>{error}</div></div>;
  if (!stockData) return <div className="not-found-container">Stock not found</div>;

  const latest = stockData.latest_price || {};
  const fundamentals = stockData.fundamentals || {};
  const priceChange = stockData.price_change ?? 0;
  const priceChangePercent = stockData.price_change_percent ?? 0;
  const chartData = stockData.price_history?.map((p) => ({
    date: p.date,
    close: parseFloat(p.close),
  })) || [];

  const isPositive = priceChange >= 0;
  const badgeClass = isPositive ? "badge-success" : "badge-danger";
  const arrowIcon = isPositive ? "↑" : "↓";

  return (
    <div className="stock-detail-container">
      <div className="header-section">
        <div className="header-content">
          <div className="title-section">
            <div className="stock-badge">{stockData.symbol}</div>
            <h1>{stockData.name}</h1>
            <div className="stock-metadata">
              <span>{stockData.exchange}</span>
              <span className="separator">•</span>
              <span>{stockData.sector?.name || 'N/A'}</span>
              <span className="separator">•</span>
              <span>{stockData.country}</span>
            </div>
          </div>
          
          <div className="price-card">
            <div className="current-price">
              <h2>{formatCurrency(latest.close)}</h2>
              <div className={`change-badge ${badgeClass}`}>
                <span className="arrow">{arrowIcon}</span>
                <span>{formatCurrency(Math.abs(priceChange))}</span>
                <span>({formatPercentage(Math.abs(priceChangePercent))})</span>
              </div>
            </div>
            <div className="trading-info">
              <div className="info-item">
                <span className="label">Volume</span>
                <span className="value">{formatNumber(latest.volume)}</span>
              </div>
              <div className="info-item">
                <span className="label">Day Range</span>
                <span className="value">{formatCurrency(latest.low)} - {formatCurrency(latest.high)}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="action-buttons">
          <button className="btn btn-primary">Add to Portfolio</button>
          <button className="btn btn-secondary">Add to Watchlist</button>
          <Link to="/" className="btn btn-tertiary">Back to Dashboard</Link>
        </div>
      </div>

      <div className="tabs-container">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab ${activeTab === 'financials' ? 'active' : ''}`}
            onClick={() => setActiveTab('financials')}
          >
            Financials
          </button>
          <button 
            className={`tab ${activeTab === 'news' ? 'active' : ''}`}
            onClick={() => setActiveTab('news')}
          >
            News
          </button>
          <button 
            className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
            onClick={() => setActiveTab('analysis')}
          >
            Analysis
          </button>
        </div>
      </div>

      <div className="stock-chart-section">
        <div className="chart-header">
          <h3>Price History</h3>
          <div className="range-selector">
            <button 
              className={`range-btn ${range === '1w' ? 'active' : ''}`} 
              onClick={() => setRange('1w')}
            >
              1W
            </button>
            <button 
              className={`range-btn ${range === '1m' ? 'active' : ''}`} 
              onClick={() => setRange('1m')}
            >
              1M
            </button>
            <button 
              className={`range-btn ${range === '1y' ? 'active' : ''}`} 
              onClick={() => setRange('1y')}
            >
              1Y
            </button>
            <button 
              className={`range-btn ${range === '3y' ? 'active' : ''}`} 
              onClick={() => setRange('3y')}
            >
              3Y
            </button>
            <button 
              className={`range-btn ${range === '5y' ? 'active' : ''}`} 
              onClick={() => setRange('5y')}
            >
              5Y
            </button>
          </div>
        </div>
        
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={isPositive ? "var(--color-positive)" : "var(--color-negative)"} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={isPositive ? "var(--color-positive)" : "var(--color-negative)"} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border-light)" />
              <XAxis 
                dataKey="date" 
                tickLine={false}
                axisLine={{ stroke: 'var(--color-border-light)' }}
                tick={{ fill: 'var(--color-text-secondary)' }}
              />
              <YAxis 
                domain={['auto', 'auto']} 
                tickLine={false}
                axisLine={{ stroke: 'var(--color-border-light)' }}
                tick={{ fill: 'var(--color-text-secondary)' }}
              />
              <Tooltip 
                formatter={(value) => formatCurrency(value)}
                contentStyle={{
                  backgroundColor: 'var(--color-background-card)',
                  borderColor: 'var(--color-border-light)',
                  borderRadius: 'var(--border-radius-small)',
                  boxShadow: 'var(--shadow-medium)'
                }}
              />
              <Area 
                type="monotone" 
                dataKey="close" 
                stroke={isPositive ? "var(--color-positive)" : "var(--color-negative)"} 
                fillOpacity={1} 
                fill="url(#colorClose)" 
                dot={false} 
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="stock-grid">
        <div className="info-card">
          <h3>Market Summary</h3>
          <div className="info-content">
            <div className="info-row">
              <span className="info-label">Previous Close</span>
              <span className="info-value">{formatCurrency(latest.close)}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Open</span>
              <span className="info-value">{formatCurrency(latest.open)}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Day Range</span>
              <span className="info-value">{formatCurrency(latest.low)} - {formatCurrency(latest.high)}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Volume</span>
              <span className="info-value">{formatNumber(latest.volume)}</span>
            </div>
          </div>
        </div>

        <div className="info-card">
          <h3>Fundamentals</h3>
          <div className="info-content">
            <div className="info-row">
              <span className="info-label">Market Cap</span>
              <span className="info-value">{formatCurrency(fundamentals.market_cap / 1_000_000)}M</span>
            </div>
            <div className="info-row">
              <span className="info-label">P/E Ratio</span>
              <span className="info-value">{fundamentals.pe_ratio?.toFixed(2) || '—'}</span>
            </div>
            <div className="info-row">
              <span className="info-label">EPS (TTM)</span>
              <span className="info-value">{formatCurrency(fundamentals.eps)}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Dividend Yield</span>
              <span className="info-value">{formatPercentage(fundamentals.dividend_yield)}</span>
            </div>
          </div>
        </div>

        <div className="info-card">
          <h3>Performance</h3>
          <div className="info-content">
            <div className="info-row">
              <span className="info-label">ROE</span>
              <span className="info-value">{formatPercentage(fundamentals.roe)}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Profit Margin</span>
              <span className="info-value">{formatPercentage(fundamentals.profit_margin)}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Price to Book</span>
              <span className="info-value">{fundamentals.price_to_book?.toFixed(2) || '—'}</span>
            </div>
            <div className="info-row">
              <span className="info-label">52-Week High/Low</span>
              <span className="info-value">N/A</span>
            </div>
          </div>
        </div>
      </div>

      <div className="stock-description-container">
        <h3>Company Description</h3>
        <div className="description-content">
          <p>{stockData.description}</p>
        </div>
      </div>

      <div className="meta-footer">
        <div className="meta-column">
          <h4>Listed In</h4>
          <div className="meta-tags">
            {stockData.indices?.map((index, i) => (
              <span key={i} className="meta-tag">{index.name}</span>
            )) || <span className="meta-tag">N/A</span>}
          </div>
        </div>
        <div className="meta-column">
          <h4>Data Source</h4>
          <p className="meta-info">Last updated: {new Date().toLocaleDateString()}</p>
        </div>
      </div>
    </div>
  );
}

export default StockDetail;