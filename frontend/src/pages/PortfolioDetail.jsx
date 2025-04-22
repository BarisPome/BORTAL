import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import PortfolioService from '../services/PortfolioService';
import PortfolioHoldings from '../components/portfolio/PortfolioHoldings';
import PortfolioTransactions from '../components/portfolio/PortfolioTransactions';
import PortfolioPerformance from '../components/portfolio/PortfolioPerformance';
import TransactionModal from '../components/portfolio/TransactionModal';
import '../styles/pages/portfolio-detail.css';
import * as StockService from '../services/stockService';



export default function PortfolioDetail() {
  const { portfolioId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [portfolios, setPortfolios] = useState([]);
  const [activePortfolio, setActivePortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('holdings'); // holdings, transactions, performance
  const [availableStocks, setAvailableStocks] = useState([]);
  const [isCreatingPortfolio, setIsCreatingPortfolio] = useState(false);
  const [isAddingTransaction, setIsAddingTransaction] = useState(false);
  const [selectedStock, setSelectedStock] = useState(null);
  const [portfolioHoldings, setPortfolioHoldings] = useState([]);
  const [refreshData, setRefreshData] = useState(0);
  const [newPortfolioName, setNewPortfolioName] = useState('');
  const [newPortfolioDescription, setNewPortfolioDescription] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: `/portfolios/${portfolioId || ''}` } });
      return;
    }
    fetchPortfolios();
    fetchAvailableStocks();
  }, [isAuthenticated, portfolioId, refreshData]);

  const fetchPortfolios = async () => {
    setLoading(true);
    try {
      const res = await PortfolioService.getPortfolios();
      const data = res.data.data;
      setPortfolios(data);

      if (data.length === 0) {
        setActivePortfolio(null);
        setIsCreatingPortfolio(true);
        return;
      }

      if (portfolioId) {
        const selected = data.find(p => p.id === portfolioId);
        if (selected) {
          setActivePortfolio(selected);
          fetchPortfolioDetail(selected.id);
        } else {
          const defaultOne = data.find(p => p.is_default) || data[0];
          setActivePortfolio(defaultOne);
          navigate(`/portfolios/${defaultOne.id}`, { replace: true });
        }
      } else {
        const defaultOne = data.find(p => p.is_default) || data[0];
        setActivePortfolio(defaultOne);
        navigate(`/portfolios/${defaultOne.id}`, { replace: true });
      }
    } catch (err) {
      setError('Portföyler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const fetchPortfolioDetail = async (id) => {
    try {
      const res = await PortfolioService.getPortfolioDetail(id);
      const portfolioData = res.data.data;
      
      // Update active portfolio with detailed data
      setActivePortfolio(portfolioData);
      
      // Set holdings data
      if (portfolioData.holdings) {
        // Enrich holdings data with more info
        const enrichedHoldings = portfolioData.holdings.map(holding => {
          // Find the latest price for each stock
          const lastPrice = holding.stock.latest_price?.close || 0;
          
          const currentValue = holding.quantity * lastPrice;
          const costValue = holding.quantity * holding.average_cost;
          const profitLoss = currentValue - costValue;
          const profitLossPercent = costValue > 0 ? (profitLoss / costValue) * 100 : 0;
          
          return {
            ...holding,
            last_price: lastPrice,
            current_value: currentValue,
            profit_loss: profitLoss,
            profit_loss_percent: profitLossPercent
          };
        });
        
        setPortfolioHoldings(enrichedHoldings);
      }
    } catch (err) {
      console.error('Error fetching portfolio detail:', err);
    }
  };

  const fetchAvailableStocks = async () => {
    try {
      const res = await StockService.getAllStocks();
      setAvailableStocks(res.data.data);
    } catch (err) {
      console.error('Error fetching stocks:', err);
    }
  };

  const createPortfolio = async (e) => {
    e.preventDefault();
    if (!newPortfolioName) return alert('Portföy adı boş olamaz');

    try {
      const res = await PortfolioService.createPortfolio({
        name: newPortfolioName,
        description: newPortfolioDescription
      });
      const newId = res.data.data.id;
      setNewPortfolioName('');
      setNewPortfolioDescription('');
      setIsCreatingPortfolio(false);
      await fetchPortfolios();
      navigate(`/portfolios/${newId}`);
    } catch (err) {
      alert(err.response?.data?.message || 'Portföy oluşturulamadı');
    }
  };

  const deletePortfolio = async () => {
    if (!activePortfolio) return;
    if (!confirm(`"${activePortfolio.name}" portföyünü silmek istiyor musunuz?`)) return;

    try {
      await PortfolioService.deletePortfolio(activePortfolio.id);
      await fetchPortfolios();
    } catch (err) {
      alert('Portföy silinemedi');
    }
  };

  const handleAddTransaction = (stock = null) => {
    setSelectedStock(stock);
    setIsAddingTransaction(true);
  };

  const handleSubmitTransaction = async (transactionData) => {
    try {
      await PortfolioService.createTransaction(activePortfolio.id, transactionData);
      setIsAddingTransaction(false);
      setSelectedStock(null);
      // Refresh data to show updated holdings and transactions
      setRefreshData(prev => prev + 1);
    } catch (err) {
      console.error('Error adding transaction:', err);
      alert(err.response?.data?.message || 'İşlem eklenemedi');
    }
  };

  const handleDeleteHolding = async (holding) => {
    if (!confirm(`"${holding.stock.symbol}" hissesini portföyden silmek istiyor musunuz?`)) return;
    
    try {
      // To delete a holding, we need to fetch all transactions for this stock
      // and delete them
      const res = await PortfolioService.getTransactions(activePortfolio.id, {
        symbol: holding.stock.symbol
      });
      
      const transactions = res.data.data;
      for (const transaction of transactions) {
        await PortfolioService.deleteTransaction(
          activePortfolio.id, 
          transaction.id
        );
      }
      
      // Refresh data
      setRefreshData(prev => prev + 1);
    } catch (err) {
      console.error('Error deleting holding:', err);
      alert('Hisse silinemedi');
    }
  };

  if (!isAuthenticated) return <div className="loading-container">Giriş yapmanız gerekiyor.</div>;
  if (loading) return <div className="loading-container">Portföyler yükleniyor...</div>;
  if (error) return <div className="error-container">{error}</div>;

  return (
    <div className="portfolio-detail-page">
      <div className="page-header">
        <h1>Portföyler</h1>
        <button className="add-portfolio-btn" onClick={() => setIsCreatingPortfolio(true)}>Yeni Portföy Oluştur</button>
      </div>

      <div className="portfolio-selector" key={portfolios.length}>
        {portfolios.map(p => (
          <button
            key={p.id}
            className={`portfolio-tab ${activePortfolio?.id === p.id ? 'active' : ''}`}
            onClick={() => {
              setActivePortfolio(p);
              navigate(`/portfolios/${p.id}`);
            }}
          >
            {p.name}
            {p.is_default && <span className="default-badge">(Varsayılan)</span>}
          </button>
        ))}
      </div>

      {activePortfolio ? (
        <div className="portfolio-container">
          <div className="portfolio-header">
            <div className="portfolio-info">
              <h2>{activePortfolio.name}</h2>
              {activePortfolio.description && <p>{activePortfolio.description}</p>}
              <div className="portfolio-meta">
                <span>Hisse Sayısı: {activePortfolio.summary?.holding_count}</span>
                <span>Toplam Değer: {activePortfolio.summary?.total_value.toLocaleString('tr-TR')} {activePortfolio.currency}</span>
                <span className={`profit-loss ${activePortfolio.summary?.profit_loss_percent >= 0 ? 'positive' : 'negative'}`}>
                  Kar/Zarar: {activePortfolio.summary?.profit_loss_percent.toFixed(2)}%
                </span>
              </div>
            </div>
            <div className="portfolio-actions">
              <button className="delete-btn" onClick={deletePortfolio}>Sil</button>
            </div>
          </div>

          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'holdings' ? 'active' : ''}`}
              onClick={() => setActiveTab('holdings')}
            >
              Hisse Senetleri
            </button>
            <button 
              className={`tab ${activeTab === 'transactions' ? 'active' : ''}`}
              onClick={() => setActiveTab('transactions')}
            >
              İşlem Geçmişi
            </button>
            <button 
              className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
              onClick={() => setActiveTab('performance')}
            >
              Performans
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'holdings' && (
              <PortfolioHoldings 
                holdings={portfolioHoldings}
                onAddTransaction={handleAddTransaction}
                onDeleteHolding={handleDeleteHolding}
              />
            )}
            
            {activeTab === 'transactions' && (
              <PortfolioTransactions 
                portfolioId={activePortfolio.id}
                onAddTransaction={() => handleAddTransaction()}
              />
            )}
            
            {activeTab === 'performance' && (
              <PortfolioPerformance portfolioId={activePortfolio.id} />
            )}
          </div>
        </div>
      ) : (
        <div className="no-portfolios">
          <h3>Henüz portföyünüz yok</h3>
        </div>
      )}

      {isCreatingPortfolio && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Yeni Portföy</h2>
            <form onSubmit={createPortfolio}>
              <div className="form-group">
                <label>Ad</label>
                <input
                  type="text"
                  value={newPortfolioName}
                  onChange={(e) => setNewPortfolioName(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Açıklama (opsiyonel)</label>
                <textarea
                  value={newPortfolioDescription}
                  onChange={(e) => setNewPortfolioDescription(e.target.value)}
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="create-btn">Oluştur</button>
                <button type="button" className="cancel-btn" onClick={() => setIsCreatingPortfolio(false)}>İptal</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isAddingTransaction && (
        <TransactionModal
          isOpen={isAddingTransaction}
          onClose={() => {
            setIsAddingTransaction(false);
            setSelectedStock(null);
          }}
          onSubmit={handleSubmitTransaction}
          initialStock={selectedStock}
          availableStocks={availableStocks}
        />
      )}
    </div>
  );
}