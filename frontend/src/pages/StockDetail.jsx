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
} from 'recharts';

function StockDetail() {
  const { symbol } = useParams();
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [range, setRange] = useState('1m'); // default: 1 month

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

  if (loading) return <div className="loading">Loading stock details...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!stockData) return <div>Stock not found</div>;

  const latest = stockData.latest_price || {};
  const fundamentals = stockData.fundamentals || {};
  const priceChange = stockData.price_change ?? 0;
  const priceChangePercent = stockData.price_change_percent ?? 0;
  const chartData = stockData.price_history?.map((p) => ({
    date: p.date,
    close: parseFloat(p.close),
  })) || [];

  return (
    <div className="stock-detail-container">
      <div className="header">
        <h1>{stockData.name} ({stockData.symbol})</h1>
        <Link to="/" className="back-link">Back to Indices</Link>
      </div>

      <div className="price-info">
        <div className="current-price">
          <h2>{formatCurrency(latest.close)}</h2>
          <span className={priceChange >= 0 ? "change positive" : "change negative"}>
            {priceChange >= 0 ? "+" : ""}{formatPercentage(priceChangePercent)}
          </span>
        </div>
      </div>

      <div className="range-selector">
        <label htmlFor="range">Price Range: </label>
        <select id="range" value={range} onChange={(e) => setRange(e.target.value)}>
          <option value="1w">1 Week</option>
          <option value="1m">1 Month</option>
          <option value="1y">1 Year</option>
          <option value="3y">3 Years</option>
          <option value="5y">5 Years</option>
        </select>
      </div>

      <div className="stock-chart">
        <h3>Price Chart ({stockData.price_range.toUpperCase()})</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <XAxis dataKey="date" />
            <YAxis domain={['auto', 'auto']} />
            <Tooltip formatter={(value) => formatCurrency(value)} />
            <Line type="monotone" dataKey="close" stroke="#4ea1f3" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="stock-grid">
        <div className="info-card">
          <h3>Market Summary</h3>
          <div className="info-row">
            <span>Previous Close</span>
            <span>{formatCurrency(latest.close)}</span>
          </div>
          <div className="info-row">
            <span>Open</span>
            <span>{formatCurrency(latest.open)}</span>
          </div>
          <div className="info-row">
            <span>Day Range</span>
            <span>{formatCurrency(latest.low)} - {formatCurrency(latest.high)}</span>
          </div>
          <div className="info-row">
            <span>Volume</span>
            <span>{formatNumber(latest.volume)}</span>
          </div>
        </div>

        <div className="info-card">
          <h3>Fundamentals</h3>
          <div className="info-row">
            <span>Market Cap</span>
            <span>{formatCurrency(fundamentals.market_cap / 1_000_000)}M</span>
          </div>
          <div className="info-row">
            <span>P/E Ratio</span>
            <span>{fundamentals.pe_ratio?.toFixed(2) || '—'}</span>
          </div>
          <div className="info-row">
            <span>EPS (TTM)</span>
            <span>{formatCurrency(fundamentals.eps)}</span>
          </div>
          <div className="info-row">
            <span>Dividend Yield</span>
            <span>{formatPercentage(fundamentals.dividend_yield)}</span>
          </div>
          <div className="info-row">
            <span>ROE</span>
            <span>{formatPercentage(fundamentals.roe)}</span>
          </div>
          <div className="info-row">
            <span>Profit Margin</span>
            <span>{formatPercentage(fundamentals.profit_margin)}</span>
          </div>
          <div className="info-row">
            <span>Price to Book</span>
            <span>{fundamentals.price_to_book?.toFixed(2) || '—'}</span>
          </div>
        </div>
      </div>

      <div className="stock-meta">
        <h3>Metadata</h3>
        <div className="info-row">
          <span>Country</span>
          <span>{stockData.country}</span>
        </div>
        <div className="info-row">
          <span>Exchange</span>
          <span>{stockData.exchange}</span>
        </div>
        <div className="info-row">
          <span>Currency</span>
          <span>{stockData.currency}</span>
        </div>
        <div className="info-row">
          <span>Sector</span>
          <span>{stockData.sector?.name || 'N/A'}</span>
        </div>
        <div className="info-row">
          <span>Indices</span>
          <span>{stockData.indices?.map(i => i.name).join(', ') || '—'}</span>
        </div>
      </div>

      <div className="stock-description">
        <h3>Company Description</h3>
        <p>{stockData.description}</p>
      </div>
    </div>
  );
}

export default StockDetail;
