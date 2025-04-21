// src/components/widgets/MarketOverviewWidget.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
///Users/barispome/Desktop/Project/BORTAL/frontend/src/styles/components/widgets/market-overview-widget.css
import '../../styles/components/widgets/market-overview-widget.css';

function MarketOverviewWidget({ marketData = {} }) {
  const [activeTab, setActiveTab] = useState('indices'); // indices, gainers, losers
  
  // Get data for each tab
  const indices = marketData.indices || [];
  const topGainers = marketData.top_gainers || [];
  const topLosers = marketData.top_losers || [];
  const marketStats = marketData.market_stats || {
    advancing: 0,
    declining: 0,
    unchanged: 0,
    total_stocks: 0
  };
  
  // Format date
  const asOfDate = marketData.as_of ? new Date(marketData.as_of) : new Date();
  const formattedDate = asOfDate.toLocaleString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  
  return (
    <div className="market-overview-widget widget">
      <div className="widget-header">
        <h2>Piyasa Genel Görünümü</h2>
        <div className="widget-header-meta">
          <span className="last-updated">Güncelleme: {formattedDate}</span>
        </div>
      </div>
      
      <div className="market-stats">
        <div className="stat-item">
          <span className="stat-label">Yükselen</span>
          <span className="stat-value positive">{marketStats.advancing}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Düşen</span>
          <span className="stat-value negative">{marketStats.declining}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Sabit</span>
          <span className="stat-value">{marketStats.unchanged}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Toplam</span>
          <span className="stat-value">{marketStats.total_stocks}</span>
        </div>
      </div>
      
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'indices' ? 'active' : ''}`}
          onClick={() => setActiveTab('indices')}
        >
          Ana Endeksler
        </button>
        <button 
          className={`tab-button ${activeTab === 'gainers' ? 'active' : ''}`}
          onClick={() => setActiveTab('gainers')}
        >
          En Çok Artanlar
        </button>
        <button 
          className={`tab-button ${activeTab === 'losers' ? 'active' : ''}`}
          onClick={() => setActiveTab('losers')}
        >
          En Çok Düşenler
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'indices' && (
          <div className="indices-tab">
            <table className="market-table">
              <thead>
                <tr>
                  <th>Endeks</th>
                  <th>Son</th>
                  <th>Değişim</th>
                </tr>
              </thead>
              <tbody>
                {indices.map((index, i) => (
                  <tr key={i}>
                    <td className="index-name">{index.display_name}</td>
                    <td className="index-price">{index.last_price.toLocaleString('tr-TR')}</td>
                    <td className={`index-change ${index.change_percent >= 0 ? 'positive' : 'negative'}`}>
                      {index.change_percent >= 0 ? '+' : ''}{index.change_percent.toFixed(2)}%
                    </td>
                  </tr>
                ))}
                
                {indices.length === 0 && (
                  <tr className="empty-row">
                    <td colSpan="3">Endeks verisi bulunamadı.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
        
        {activeTab === 'gainers' && (
          <div className="gainers-tab">
            <table className="market-table">
              <thead>
                <tr>
                  <th>Sembol</th>
                  <th>Fiyat</th>
                  <th>Değişim</th>
                </tr>
              </thead>
              <tbody>
                {topGainers.map((stock, i) => (
                  <tr key={i}>
                    <td className="stock-name">
                      <Link to={`/stock/${stock.symbol}`}>
                        <div className="stock-symbol">{stock.symbol}</div>
                        <div className="stock-company">{stock.name}</div>
                      </Link>
                    </td>
                    <td className="stock-price">{stock.price.toLocaleString('tr-TR')}</td>
                    <td className="stock-change positive">+{stock.change_percent.toFixed(2)}%</td>
                  </tr>
                ))}
                
                {topGainers.length === 0 && (
                  <tr className="empty-row">
                    <td colSpan="3">Veri bulunamadı.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
        
        {activeTab === 'losers' && (
          <div className="losers-tab">
            <table className="market-table">
              <thead>
                <tr>
                  <th>Sembol</th>
                  <th>Fiyat</th>
                  <th>Değişim</th>
                </tr>
              </thead>
              <tbody>
                {topLosers.map((stock, i) => (
                  <tr key={i}>
                    <td className="stock-name">
                      <Link to={`/stock/${stock.symbol}`}>
                        <div className="stock-symbol">{stock.symbol}</div>
                        <div className="stock-company">{stock.name}</div>
                      </Link>
                    </td>
                    <td className="stock-price">{stock.price.toLocaleString('tr-TR')}</td>
                    <td className="stock-change negative">{stock.change_percent.toFixed(2)}%</td>
                  </tr>
                ))}
                
                {topLosers.length === 0 && (
                  <tr className="empty-row">
                    <td colSpan="3">Veri bulunamadı.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default MarketOverviewWidget;