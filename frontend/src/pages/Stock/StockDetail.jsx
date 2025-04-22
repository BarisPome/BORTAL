import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getStockDetail } from '../../services/stockService';
import { formatCurrency, formatNumber, formatPercentage } from '../../utils/formatters';
import StockNewsWidget from '../../components/widgets/StockNewsWidget';
///Users/barispome/Desktop/Project/BORTAL/frontend/src/styles/pages/stock-detail.css

import '../../styles/pages/stock-detail.css';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

export default function StockDetail() {
  const { symbol } = useParams();
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [range, setRange] = useState('1m');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchStockDetail = async () => {
      setLoading(true);
      try {
        const data = await getStockDetail(symbol, range);
        setStockData(data);
      } catch (err) {
        console.error('Error fetching stock details:', err);
        setError(`Error fetching data for ${symbol}: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    fetchStockDetail();
  }, [symbol, range]);

  if (loading) return <div className="loading-container"><div className="loading-spinner"/>Loading stock details...</div>;
  if (error) return <div className="error-container">⚠️ {error}</div>;
  if (!stockData) return <div className="not-found-container">Stock not found</div>;

  const { latest_price: latest = {}, fundamentals = {}, price_history: history = [] } = stockData;
  const priceChange = stockData.price_change ?? 0;
  const priceChangePercent = stockData.price_change_percent ?? 0;
  const chartData = history.map(p => ({ date: p.date, close: parseFloat(p.close) }));
  const isPositive = priceChange >= 0;
  const badgeClass = isPositive ? 'badge-success' : 'badge-danger';
  const arrowIcon = isPositive ? '↑' : '↓';

  return (
    <div className="stock-detail-container">
      <header className="detail-header">
        <h1>{stockData.symbol} - {stockData.name}</h1>
        <Link to="/" className="back-link">← Back</Link>
      </header>

      <div className="tabs-container">
        {['overview','financials','news','analysis'].map(tab => (
          <button
            key={tab}
            className={`tab-button ${activeTab===tab?'active':''}`}
            onClick={() => setActiveTab(tab)}
          >{tab.charAt(0).toUpperCase()+tab.slice(1)}</button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <section className="overview-section">
          <div className="price-card">
            <div className="current-price">
              <h2>{formatCurrency(latest.close)}</h2>
              <span className={`change-badge ${badgeClass}`}>
                {arrowIcon}{formatCurrency(Math.abs(priceChange))} ({formatPercentage(Math.abs(priceChangePercent))})
              </span>
            </div>
            <div className="trading-info">
              <div><strong>Volume:</strong> {formatNumber(latest.volume)}</div>
              <div><strong>Day Range:</strong> {formatCurrency(latest.low)} - {formatCurrency(latest.high)}</div>
            </div>
          </div>

          <div className="chart-section">
            <h3>Price History</h3>
            <div className="range-selector">
              {['1w','1m','1y','3y','5y'].map(r=> (
                <button
                  key={r}
                  className={range===r?'active':''}
                  onClick={()=>setRange(r)}
                >{r.toUpperCase()}</button>
              ))}
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={isPositive?'var(--color-positive)':'var(--color-negative)'} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={isPositive?'var(--color-positive)':'var(--color-negative)'} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={val=>formatCurrency(val)} />
                <Area type="monotone" dataKey="close" stroke={isPositive?'var(--color-positive)':'var(--color-negative)'} fill="url(#grad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="description">
            <h3>Company Description</h3>
            <p>{stockData.description}</p>
          </div>
        </section>
      )}

      {activeTab === 'financials' && (
        <section className="financials-section">
          <h3>Financials & Metrics</h3>
          <div className="metrics-grid">
            <div><strong>Market Cap:</strong> {formatCurrency(fundamentals.market_cap)}</div>
            <div><strong>P/E Ratio:</strong> {fundamentals.pe_ratio?.toFixed(2)||'—'}</div>
            <div><strong>EPS (TTM):</strong> {formatCurrency(fundamentals.eps)}</div>
            <div><strong>Dividend Yield:</strong> {formatPercentage(fundamentals.dividend_yield)}</div>
            <div><strong>ROE:</strong> {formatPercentage(fundamentals.roe)}</div>
            <div><strong>Profit Margin:</strong> {formatPercentage(fundamentals.profit_margin)}</div>
            <div><strong>Price/Book:</strong> {fundamentals.price_to_book?.toFixed(2)||'—'}</div>
          </div>
        </section>
      )}

      {activeTab === 'news' && (
        <section className="news-section">
          <StockNewsWidget symbol={symbol} />
        </section>
      )}

      {activeTab === 'analysis' && (
        <section className="analysis-section">
          <StockTechnicalWidget symbol={symbol} />
        </section>
      )}

    </div>
  );
}