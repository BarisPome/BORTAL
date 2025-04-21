// src/components/widgets/WatchlistWidget.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import '../../styles/components/widgets/watchlist-widget.css';



function WatchlistWidget({ watchlists = [] }) {
  const [activeWatchlist, setActiveWatchlist] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Set the default watchlist as active or the first one
    if (watchlists.length > 0) {
      const defaultWatchlist = watchlists.find(watchlist => watchlist.is_default) || watchlists[0];
      setActiveWatchlist(defaultWatchlist);
    }
  }, [watchlists]);

  if (watchlists.length === 0) {
    return (
      <div className="watchlist-widget widget empty-state">
        <div className="widget-header">
          <h2>İzleme Listem</h2>
          <button className="add-list-btn">+ Yeni Liste Oluştur</button>
        </div>
        <div className="empty-watchlist">
          <div className="empty-icon">📋</div>
          <p>Henüz izleme listeniz bulunmuyor.</p>
          <button className="btn primary">İzleme Listesi Oluştur</button>
        </div>
      </div>
    );
  }

  return (
    <div className="watchlist-widget widget">
      <div className="widget-header">
        <h2>İzleme Listem</h2>
        <div className="widget-actions">
          <button className="add-stock-btn">+ Hisse Ekle</button>
          <Link to="/watchlists" className="view-all">Tümünü Gör</Link>
        </div>
      </div>
      
      {watchlists.length > 1 && (
        <div className="watchlist-selector">
          {watchlists.map(watchlist => (
            <button
              key={watchlist.id}
              className={`watchlist-tab ${activeWatchlist?.id === watchlist.id ? 'active' : ''}`}
              onClick={() => setActiveWatchlist(watchlist)}
            >
              {watchlist.name} ({watchlist.stock_count})
            </button>
          ))}
        </div>
      )}
      
      <div className="watchlist-table">
        <div className="watchlist-header">
          <div className="column-heading symbol">Sembol</div>
          <div className="column-heading price">Son Fiyat</div>
          <div className="column-heading change">Değişim</div>
        </div>
        
        <div className="watchlist-body">
          {activeWatchlist?.top_stocks?.map((stock, index) => (
            <Link to={`/stock/${stock.symbol}`} key={index} className="watchlist-item">
              <div className="stock-info">
                <div className="stock-symbol">{stock.symbol}</div>
                <div className="stock-name">{stock.name}</div>
              </div>
              <div className="stock-price">{stock.price.toLocaleString('tr-TR')} ₺</div>
              <div className={`stock-change ${stock.change_percent >= 0 ? 'positive' : 'negative'}`}>
                {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
              </div>
            </Link>
          ))}
          
          {activeWatchlist?.top_stocks?.length === 0 && (
            <div className="empty-watchlist-items">
              <p>Bu izleme listesinde hisse senedi bulunmuyor.</p>
              <button className="btn primary sm">Hisse Ekle</button>
            </div>
          )}
        </div>
      </div>
      
      <div className="watchlist-footer">
        <button className="btn secondary">Listeyi Düzenle</button>
      </div>
    </div>
  );
}

export default WatchlistWidget;