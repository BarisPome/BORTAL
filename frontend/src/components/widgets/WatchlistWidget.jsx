
///BORTAL/frontend/src/components/widgets/WatchlistWidget.jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../services/apiClient';
import '../../styles/components/widgets/watchlist-widget.css';

export default function WatchlistWidget() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [watchlists, setWatchlists] = useState([]);
  const [expanded, setExpanded] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    setLoading(true);
    api.get('watchlists/')
      .then(response => {
        const lists = response.data.data;
        setWatchlists(lists);

        // Başlangıçta tümü açık
        const initialExpanded = {};
        lists.forEach(list => {
          initialExpanded[list.id] = true;
        });
        setExpanded(initialExpanded);
      })
      .catch(err => {
        setError(
          err.response?.data?.message || err.response?.data?.detail || err.message || 'İzleme listeleri yüklenemedi.'
        );
      })
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  const toggleExpanded = (id) => {
    setExpanded(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const navigateToWatchlistCreation = () => {
    navigate('/watchlists', { state: { createNew: true } });
  };

  if (!isAuthenticated) return <div className="widget">Lütfen giriş yapın.</div>;
  if (loading) return <div className="widget">Yükleniyor...</div>;
  if (error) return <div className="widget error">Hata: {error}</div>;
  if (watchlists.length === 0) {
    return (
      <div className="watchlist-widget widget">
        <div className="widget-header">
          <h2>İzleme Listem</h2>
        </div>
        <div className="empty-state">
          <p>Henüz bir izleme listeniz bulunmuyor.</p>
          <button 
            className="create-watchlist-button"
            onClick={navigateToWatchlistCreation}
          >
            Yeni İzleme Listesi Oluştur
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="watchlist-widget widget">
      <div className="widget-header">
        <h2>İzleme Listelerim</h2>
        <Link to="/watchlists" className="view-all-link">Tümünü Gör</Link>
      </div>

      {watchlists.map(watchlist => (
        <div key={watchlist.id} className="watchlist-block">
          <div 
            className="watchlist-title"
            onClick={() => toggleExpanded(watchlist.id)}
          >
            <strong>{watchlist.name}</strong>
            {watchlist.is_default && <span className="default-badge"> (Varsayılan)</span>}
            <span className="toggle-icon">{expanded[watchlist.id] ? '▲' : '▼'}</span>
          </div>

          {expanded[watchlist.id] && (
            <div className="watchlist-body">
              {watchlist.stocks.length > 0 ? (
                watchlist.stocks.map(stock => (
                  <div
                    key={stock.id}
                    className="watchlist-item"
                    onClick={() => navigate(`/stock/${stock.symbol}`)}
                  >
                    <div className="stock-symbol">{stock.symbol}</div>
                    <div className="stock-name">{stock.name}</div>
                    <div className="stock-price">
                      {stock.latest_price
                        ? stock.latest_price.price.toLocaleString('tr-TR') + ' ₺'
                        : '—'}
                    </div>
                    <div className={`stock-change ${stock.latest_price && stock.latest_price.change_percent >= 0 ? 'positive' : 'negative'}`}>
                      {stock.latest_price
                        ? (stock.latest_price.change_percent >= 0 ? '+' : '') + stock.latest_price.change_percent.toFixed(2) + '%'
                        : '—'}
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-watchlist-message">
                  <p>Bu izleme listesinde hisse senedi bulunmuyor.</p>
                  <Link to={`/watchlists/${watchlist.id}`} className="add-stocks-link">
                    Hisse Ekle
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
