// src/components/widgets/WatchlistWidget.jsx
import { Link } from 'react-router-dom';
import '../../styles/components/widgets/watchlist-widget.css';
import StockDetail from '../../pages/StockDetail';

function WatchlistWidget() {
  const watchlistItems = [
    { symbol: 'AKBNK', name: 'Akbank', price: 23.45, change: 1.25, percentChange: 5.62, positive: true },
    { symbol: 'THYAO', name: 'Turkish Airlines', price: 55.70, change: -2.30, percentChange: -3.96, positive: false },
    { symbol: 'SASA', name: 'SASA Polyester', price: 42.18, change: 3.42, percentChange: 8.82, positive: true },
    { symbol: 'EREGL', name: 'Ereğli Iron', price: 36.90, change: 0.70, percentChange: 1.93, positive: true },
    { symbol: 'GARAN', name: 'Garanti Bank', price: 18.75, change: -0.45, percentChange: -2.34, positive: false },
  ];
  
  return (
    <div className="widget watchlist-widget">
      <div className="widget-header">
        <h3>My Watchlist</h3>
        <div className="widget-controls">
          <button className="widget-control">
            <span className="control-icon add"></span>
          </button>
          <button className="widget-control">
            <span className="control-icon expand"></span>
          </button>
        </div>
      </div>
      
      <div className="watchlist-items">
        {watchlistItems.map(item => (
          <Link to={`/stock/${item.symbol}`} key={item.symbol} className="watchlist-item">
            <div className="stock-info">
              <div className="stock-symbol">{item.symbol}</div>
              <div className="stock-name">{item.name}</div>
            </div>
            <div className="stock-price">{item.price.toFixed(2)}</div>
            <div className={`stock-change ${item.positive ? 'positive' : 'negative'}`}>
              {item.positive ? '+' : ''}{item.change.toFixed(2)} ({item.percentChange.toFixed(2)}%)
            </div>
          </Link>
        ))}
      </div>
      
      <div className="widget-footer">
        <button className="watchlist-manage-btn">Manage Watchlist</button>
      </div>
    </div>
  );
}

export default WatchlistWidget;