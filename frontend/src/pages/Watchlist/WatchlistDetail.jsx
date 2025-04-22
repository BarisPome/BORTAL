// /src/pages/WatchlistDetail.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation} from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/apiClient';
import '../../styles/pages/watchlist-detail.css';

export default function WatchlistDetail() {
  const { watchlistId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [watchlists, setWatchlists] = useState([]);
  const [activeWatchlist, setActiveWatchlist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isCreatingWatchlist, setIsCreatingWatchlist] = useState(false);
  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [newWatchlistDescription, setNewWatchlistDescription] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: `/watchlists/${watchlistId || ''}` } });
      return;
    }

    fetchWatchlists();
  }, [isAuthenticated, watchlistId, location]);

  const fetchWatchlists = async () => {
    setLoading(true);
    try {
      const response = await api.get('watchlists/');
      const lists = response.data.data;
      console.log('Fetched watchlists:', lists);
      setWatchlists(lists);

      if (lists.length === 0) {
        setActiveWatchlist(null);
        setIsCreatingWatchlist(true);
        if (location.state?.createNew) {
          navigate(location.pathname, { replace: true });
        }
        return;
      }

      if (watchlistId) {
        const selected = lists.find(w => w.id === watchlistId);
        if (selected) {
          setActiveWatchlist(selected);
        } else {
          const defaultList = lists.find(w => w.is_default) || lists[0];
          setActiveWatchlist(defaultList);
          navigate(`/watchlists/${defaultList.id}`, { replace: true });
        }
      } else {
        const defaultList = lists.find(w => w.is_default) || lists[0];
        setActiveWatchlist(defaultList);
        navigate(`/watchlists/${defaultList.id}`, { replace: true });
      }
    } catch (err) {
      console.error('Error fetching watchlists:', err);
      setError(err.response?.data?.message || err.response?.data?.detail || err.message || 'İzleme listeleri yüklenemedi.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm) return;

    setIsSearching(true);
    try {
      const response = await api.get(`stocks/?search=${searchTerm}`);
      setSearchResults(response.data.data || []);
    } catch (err) {
      console.error('Arama hatası:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const addStockToWatchlist = async (symbol) => {
    if (!activeWatchlist) return;

    try {
      await api.post(`watchlists/${activeWatchlist.id}/stocks/`, { symbol });
      fetchWatchlists();
      setSearchTerm('');
      setSearchResults([]);
    } catch (err) {
      alert(err.response?.data?.message || err.response?.data?.detail || 'Hisse senedi eklenemedi');
    }
  };

  const removeStockFromWatchlist = async (symbol) => {
    if (!activeWatchlist) return;
    if (!confirm(`${symbol} listesinden çıkarılsın mı?`)) return;

    try {
      await api.delete(`watchlists/${activeWatchlist.id}/stocks/${symbol}/`);
      fetchWatchlists();
    } catch (err) {
      alert(err.response?.data?.message || err.response?.data?.detail || 'Hisse senedi izleme listesinden çıkarılamadı');
    }
  };

  const createWatchlist = async (e) => {
    e.preventDefault();
    if (!newWatchlistName) {
      alert('İzleme listesi adı gerekli');
      return;
    }

    try {
      const response = await api.post('watchlists/', {
        name: newWatchlistName,
        description: newWatchlistDescription
      });
      await fetchWatchlists();
      setIsCreatingWatchlist(false);
      setNewWatchlistName('');
      setNewWatchlistDescription('');
      const newWatchlistId = response.data.data.id;
      window.location.href = `/watchlists/${newWatchlistId}`;
    } catch (err) {
      alert(err.response?.data?.message || err.response?.data?.detail || 'İzleme listesi oluşturulamadı');
    }
  };

  const deleteWatchlist = async () => {
    if (!activeWatchlist) return;
    if (watchlists.length === 1) {
      if (!confirm('Bu tek izleme listeniz. Silmek istediğinize emin misiniz?')) return;
    } else {
      if (!confirm(`"${activeWatchlist.name}" izleme listesini silmek istediğinize emin misiniz?`)) return;
    }

    try {
      await api.delete(`watchlists/${activeWatchlist.id}/`);
      fetchWatchlists();
    } catch (err) {
      alert(err.response?.data?.message || err.response?.data?.detail || 'İzleme listesi silinemedi');
    }
  };

  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');

  const startEditing = () => {
    if (!activeWatchlist) return;
    setEditName(activeWatchlist.name);
    setEditDescription(activeWatchlist.description || '');
    setIsEditing(true);
  };

  const saveWatchlistChanges = async (e) => {
    e.preventDefault();
    if (!activeWatchlist) return;
    if (!editName) {
      alert('İzleme listesi adı boş olamaz');
      return;
    }

    try {
      await api.put(`watchlists/${activeWatchlist.id}/`, {
        name: editName,
        description: editDescription
      });
      fetchWatchlists();
      setIsEditing(false);
    } catch (err) {
      alert(err.response?.data?.message || err.response?.data?.detail || 'İzleme listesi güncellenemedi');
    }
  };

  useEffect(() => {
    if (watchlistId && watchlists.length > 0) {
      const selected = watchlists.find(w => w.id === watchlistId);
      if (selected) {
        setActiveWatchlist(selected);
      }
    }
  }, [watchlistId, watchlists]);

  if (!isAuthenticated) {
    return <div className="loading-container">Lütfen izleme listelerinizi görüntülemek için giriş yapın.</div>;
  }

  if (loading) {
    return <div className="loading-container">İzleme listeleri yükleniyor...</div>;
  }

  if (error) {
    return <div className="error-container">Hata: {error}</div>;
  }

  return (
    <div className="watchlist-detail-page">
      <div className="page-header">
        <h1>İzleme Listeleri</h1>
        <button className="add-watchlist-btn" onClick={() => setIsCreatingWatchlist(true)}>
          Yeni Liste Oluştur
        </button>
      </div>

      <div className="watchlist-selector" key={watchlists.length}>
        {watchlists.map(watchlist => (
          <button
            key={watchlist.id}
            className={`watchlist-tab ${activeWatchlist?.id === watchlist.id ? 'active' : ''}`}
            onClick={() => {
              setActiveWatchlist(watchlist);
              navigate(`/watchlists/${watchlist.id}`);
            }}
          >
            {watchlist.name}
            {watchlist.is_default && <span className="default-badge">(Varsayılan)</span>}
          </button>
        ))}
      </div>

      {activeWatchlist ? (
        <div className="watchlist-container">
          <div className="watchlist-header">
            {isEditing ? (
              <form onSubmit={saveWatchlistChanges} className="edit-watchlist-form">
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  placeholder="İzleme listesi adı"
                  className="edit-watchlist-name"
                  required
                />
                <textarea
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="Açıklama (isteğe bağlı)"
                  className="edit-watchlist-description"
                />
                <div className="edit-actions">
                  <button type="submit" className="save-btn">Kaydet</button>
                  <button type="button" className="cancel-btn" onClick={() => setIsEditing(false)}>İptal</button>
                </div>
              </form>
            ) : (
              <>
                <div className="watchlist-info">
                  <h2>{activeWatchlist.name}</h2>
                  {activeWatchlist.description && <p className="watchlist-description">{activeWatchlist.description}</p>}
                  <div className="watchlist-meta">
                    <span>{activeWatchlist.stocks.length} hisse</span>
                    <span>Oluşturulma: {new Date(activeWatchlist.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="watchlist-actions">
                  <button className="edit-btn" onClick={startEditing}>Düzenle</button>
                  <button className="delete-btn" onClick={deleteWatchlist}>Sil</button>
                </div>
              </>
            )}
          </div>

          <div className="search-section">
            <form onSubmit={handleSearch} className="stock-search-form">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Hisse ara..."
                className="stock-search-input"
              />
              <button type="submit" className="search-btn" disabled={isSearching}>
                {isSearching ? 'Aranıyor...' : 'Ara'}
              </button>
            </form>

            {searchResults.length > 0 && (
              <div className="search-results">
                <h3>Arama Sonuçları</h3>
                <div className="results-list">
                  {searchResults.map(stock => {
                    const isInWatchlist = activeWatchlist.stocks.some(s => s.symbol === stock.symbol);
                    return (
                      <div key={stock.id} className="search-result-item">
                        <div className="stock-info">
                          <div className="stock-symbol">{stock.symbol}</div>
                          <div className="stock-name">{stock.name}</div>
                        </div>
                        <button
                          className={`add-stock-btn ${isInWatchlist ? 'disabled' : ''}`}
                          onClick={() => addStockToWatchlist(stock.symbol)}
                          disabled={isInWatchlist}
                        >
                          {isInWatchlist ? 'Zaten Eklendi' : 'Ekle'}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          <div className="watchlist-stocks">
            <h3>İzleme Listesindeki Hisseler</h3>
            {activeWatchlist.stocks.length === 0 ? (
              <div className="empty-watchlist">
                <p>Bu izleme listesi boş. Hisse eklemek için yukarıdan arama yapabilirsiniz.</p>
              </div>
            ) : (
              <div className="stocks-table">
                <div className="stocks-header">
                  <div className="col">Sembol</div>
                  <div className="col">Ad</div>
                  <div className="col">Fiyat</div>
                  <div className="col">Değişim</div>
                  <div className="col actions">İşlemler</div>
                </div>
                <div className="stocks-body">
                  {activeWatchlist.stocks.map(stock => (
                    <div key={stock.id} className="stock-row">
                      <div className="col stock-symbol">{stock.symbol}</div>
                      <div className="col stock-name">{stock.name}</div>
                      <div className="col stock-price">
                        {stock.latest_price ? stock.latest_price.price.toLocaleString('tr-TR') + ' ₺' : '—'}
                      </div>
                      <div className={`col stock-change ${stock.latest_price && stock.latest_price.change_percent >= 0 ? 'positive' : 'negative'}`}>
                        {stock.latest_price ? (stock.latest_price.change_percent >= 0 ? '+' : '') + stock.latest_price.change_percent.toFixed(2) + '%' : '—'}
                      </div>
                      <div className="col actions">
                        <Link to={`/stock/${stock.symbol}`} className="view-btn">Görüntüle</Link>
                        <button className="remove-btn" onClick={() => removeStockFromWatchlist(stock.symbol)}>Kaldır</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="no-watchlists">
          <div className="empty-state">
            <h3>Henüz izleme listeniz yok</h3>
            <p>İzleme listeleri favori hisselerinizi takip etmenizi sağlar.</p>
            <button className="create-watchlist-btn" onClick={() => setIsCreatingWatchlist(true)}>
              İlk İzleme Listenizi Oluşturun
            </button>
          </div>
        </div>
      )}

      {isCreatingWatchlist && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Yeni İzleme Listesi Oluştur</h2>
            <form onSubmit={createWatchlist} className="create-watchlist-form">
              <div className="form-group">
                <label htmlFor="watchlist-name">Liste Adı</label>
                <input
                  type="text"
                  id="watchlist-name"
                  value={newWatchlistName}
                  onChange={(e) => setNewWatchlistName(e.target.value)}
                  placeholder="Liste adı girin"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="watchlist-description">Açıklama (isteğe bağlı)</label>
                <textarea
                  id="watchlist-description"
                  value={newWatchlistDescription}
                  onChange={(e) => setNewWatchlistDescription(e.target.value)}
                  placeholder="Bir açıklama girin"
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="create-btn">Oluştur</button>
                <button type="button" className="cancel-btn" onClick={() => setIsCreatingWatchlist(false)}>
                  İptal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}