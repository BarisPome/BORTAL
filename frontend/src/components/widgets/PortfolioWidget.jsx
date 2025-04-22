// src/components/widgets/PortfolioWidget.jsx
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../../styles/components/widgets/portfolioWidget.css';
import PortfolioService from '../../services/PortfolioService';

function PortfolioWidget() {
  const [portfolios, setPortfolios] = useState([]);
  const [activePortfolio, setActivePortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPortfolios = async () => {
      try {
        const response = await PortfolioService.getPortfolios();
        const data = response.data.data;
        setPortfolios(data);
        const defaultPortfolio = data.find(p => p.is_default) || data[0];
        setActivePortfolio(defaultPortfolio);
      } catch (err) {
        console.error('Portföyler yüklenemedi:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolios();
  }, []);

  const goToCreatePage = () => {
    navigate('/portfolios', { state: { createNew: true } });
  };

  if (loading) {
    return <div className="portfolio-widget widget">Yükleniyor...</div>;
  }

  if (portfolios.length === 0) {
    return (
      <div className="portfolio-widget widget empty-state">
        <div className="widget-header">
          <h2>Portföyüm</h2>
          <button className="add-portfolio-btn" onClick={goToCreatePage}>+ Yeni Portföy</button>
        </div>
        <div className="empty-portfolio">
          <div className="empty-icon">💼</div>
          <p>Henüz portföyünüz bulunmuyor.</p>
          <button className="btn primary" onClick={goToCreatePage}>Portföy Oluştur</button>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio-widget widget">
      <div className="widget-header">
        <h2>Portföyüm</h2>
        <Link to="/portfolios" className="view-all">Tümünü Gör</Link>
      </div>

      {portfolios.length > 1 && (
        <div className="portfolio-selector">
          {portfolios.map(portfolio => (
            <button
              key={portfolio.id}
              className={`portfolio-tab ${activePortfolio?.id === portfolio.id ? 'active' : ''}`}
              onClick={() => setActivePortfolio(portfolio)}
            >
              {portfolio.name}
            </button>
          ))}
        </div>
      )}

      <div className="portfolio-summary">
        <div className="portfolio-value">
          <span className="label">Toplam Değer</span>
          <span className="value">
            {activePortfolio?.summary?.total_value?.toLocaleString('tr-TR')} {activePortfolio?.currency || '₺'}
          </span>
        </div>
        <div className="portfolio-change">
          <span className="label">Toplam Kar/Zarar</span>
          <span className={`value ${activePortfolio?.summary?.profit_loss_percent >= 0 ? 'positive' : 'negative'}`}>
            {activePortfolio?.summary?.profit_loss_percent >= 0 ? '+' : ''}
            {activePortfolio?.summary?.profit_loss_percent?.toFixed(2)}%
          </span>
        </div>
      </div>

      <div className="portfolio-holdings">
        <div className="holdings-header">
          <span className="column-heading symbol">Sembol</span>
          <span className="column-heading shares">Adet</span>
          <span className="column-heading price">Değer</span>
          <span className="column-heading weight">Ağırlık</span>
        </div>

        <div className="holdings-list">
          {activePortfolio?.top_holdings?.length > 0 ? (
            activePortfolio.top_holdings.map((holding, index) => (
              <Link to={`/stock/${holding.symbol}`} key={index} className="holding-item">
                <div className="stock-info">
                  <span className="stock-symbol">{holding.symbol}</span>
                  <span className="stock-name">{holding.name}</span>
                </div>
                <div className="shares">{holding.quantity}</div>
                <div className="value">
                  {holding.value?.toLocaleString('tr-TR')} {activePortfolio.currency}
                </div>
                <div className="weight">{holding.weight?.toFixed(1)}%</div>
              </Link>
            ))
          ) : (
            <div className="empty-holdings">
              <p>Bu portföyde hisse bulunmuyor.</p>
              <button className="btn primary sm" onClick={() => navigate('/portfolios')}>Hisse Ekle</button>
            </div>
          )}
        </div>
      </div>

      <div className="portfolio-actions">
        <button className="btn primary" onClick={() => navigate('/portfolios')}>Hisse Ekle</button>
        <button className="btn secondary" onClick={() => navigate('/portfolios')}>İşlem Geçmişi</button>
      </div>
    </div>
  );
}

export default PortfolioWidget;
