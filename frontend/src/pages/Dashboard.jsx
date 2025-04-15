// src/pages/Dashboard.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/pages/dashboard.css';
import MarketOverviewWidget from '../components/widgets/MarketOverviewWidget';
import IndexPerformanceWidget from '../components/widgets/IndexPerformanceWidget';
import WatchlistWidget from '../components/widgets/WatchlistWidget';
import StockNewsWidget from '../components/widgets/StockNewsWidget';
import TechnicalAnalysisWidget from '../components/widgets/TechnicalAnalysisWidget';

function Dashboard() {
  const [selectedIndex, setSelectedIndex] = useState('BIST100');
  
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Market Dashboard</h1>
        <div className="market-status">
          <div className="market-indicator online"></div>
          <span>Market Open</span>
          <span className="market-time">14:35:22</span>
        </div>
      </div>
      
      <div className="index-selector-container">
        <div className="index-selector">
          {[
            'BIST100', 
            'BIST50', 
            'BIST30', 
            'BIST_KOBI_SANAYI', 
            'BIST_SINAI', 
            'BIST_GIDA_ICECEK', 
            'BIST_KIMYA_PETROL_PLASTIK',
            'BIST_MADENCILIK', 
            'BIST_METAL_ESYA_MAKINA', 
            'BIST_ORMAN_KAGIT_BASIM', 
            'BIST_TAS_TOPRAK',
            'BIST_TEKSTIL_DERI', 
            'BIST_HIZMETLER', 
            'BIST_BANKA'
          ].map(index => (
            <button
              key={index}
              className={selectedIndex === index ? 'active' : ''}
              onClick={() => setSelectedIndex(index)}
            >
              {index.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>
      
      <div className="dashboard-grid">
        <div className="dashboard-column main-column">
          <IndexPerformanceWidget indexName={selectedIndex} />
          <MarketOverviewWidget />
        </div>
        
        <div className="dashboard-column side-column">
          <WatchlistWidget />
          <StockNewsWidget />
          <TechnicalAnalysisWidget />
        </div>
      </div>
      
      <div className="top-movers">
        <h2>Top Movers</h2>
        <div className="movers-tabs">
          <button className="active">Gainers</button>
          <button>Losers</button>
          <button>Volume</button>
        </div>
        
        <div className="movers-list">
          {[1, 2, 3, 4, 5].map(index => (
            <Link to={`/stock/STOCK${index}`} key={index} className="mover-card">
              <div className="mover-symbol">STOCK{index}</div>
              <div className="mover-name">Company Name {index}</div>
              <div className="mover-change positive">+{(Math.random() * 5).toFixed(2)}%</div>
            </Link>
          ))}
        </div>
      </div>
      
      <div className="recent-activity">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          <div className="activity-item">
            <div className="activity-icon view"></div>
            <div className="activity-details">
              <span className="activity-stock">AKBNK</span>
              <span className="activity-action">Viewed details</span>
            </div>
            <div className="activity-time">5m ago</div>
          </div>
          <div className="activity-item">
            <div className="activity-icon analysis"></div>
            <div className="activity-details">
              <span className="activity-stock">THYAO</span>
              <span className="activity-action">Technical analysis</span>
            </div>
            <div className="activity-time">22m ago</div>
          </div>
          <div className="activity-item">
            <div className="activity-icon watchlist"></div>
            <div className="activity-details">
              <span className="activity-stock">SASA</span>
              <span className="activity-action">Added to watchlist</span>
            </div>
            <div className="activity-time">1h ago</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;