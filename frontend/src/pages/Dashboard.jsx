// src/pages/Dashboard.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import '../styles/pages/dashboard.css';
import MarketOverviewWidget from '../components/widgets/MarketOverviewWidget';
import IndexPerformanceWidget from '../components/widgets/IndexPerformanceWidget';
import WatchlistWidget from '../components/widgets/WatchlistWidget';
import StockNewsWidget from '../components/widgets/StockNewsWidget';
import TechnicalAnalysisWidget from '../components/widgets/TechnicalAnalysisWidget';
import PortfolioWidget from '../components/widgets/PortfolioWidget';
import { getDashboardData } from '../services/dashboardService';

// Import mock data as fallback
import { MOCK_DASHBOARD_DATA } from '../mock/dashboardData';

function Dashboard() {
  const [selectedIndex, setSelectedIndex] = useState('BIST100');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [useMockData, setUseMockData] = useState(false);
  const [activeMoversTab, setActiveMoversTab] = useState('gainers'); // gainers, losers, volume
  
  // Get current time for market status display
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // Fetch dashboard data on component mount
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        console.log('Attempting to fetch dashboard data...');
        
        try {
          // First try to get data from the API
          const response = await getDashboardData();
          console.log('API response:', response);
          if (response && response.data) {
            setDashboardData(response.data);
            setUseMockData(false);
            setLoading(false);
            return;
          }
        } catch (apiError) {
          console.error('API error:', apiError);
          // Fall back to mock data if API fails
        }
        
        // If we're here, API failed - use mock data
        setDashboardData(MOCK_DASHBOARD_DATA);
        setUseMockData(true);
        setLoading(false);
      } catch (err) {
        console.error('Error in dashboard loading:', err);
        setError('Failed to load dashboard data. Please try again.');
        setLoading(false);
      }
    };
    
    fetchDashboardData();
    
    // Update time every minute
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    
    return () => clearInterval(timeInterval);
  }, []);
  
  // Format time for display (HH:MM:SS)
  const formatTime = (date) => {
    return date.toLocaleTimeString('tr-TR', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false
    });
  };
  
  // Format date for display (DD.MM.YYYY)
  const formatDate = (date) => {
    return date.toLocaleDateString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };
  
  // Check if market is open (9:30 AM to 6:00 PM on weekdays)
  const isMarketOpen = () => {
    const now = currentTime;
    const day = now.getDay();
    const hour = now.getHours();
    const minute = now.getMinutes();
    
    // Market is closed on weekends (Saturday=6, Sunday=0)
    if (day === 0 || day === 6) {
      return false;
    }
    
    // Market hours: 9:30 AM - 6:00 PM
    if ((hour > 9 || (hour === 9 && minute >= 30)) && hour < 18) {
      return true;
    }
    
    return false;
  };
  
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <div>Loading dashboard data...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <div>{error}</div>
        <button 
          className="btn primary" 
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    );
  }
  
  // Extract data for components
  const marketOverviewData = dashboardData?.market_overview || {};
  const userWatchlists = dashboardData?.user_watchlists || [];
  const userPortfolios = dashboardData?.user_portfolios || [];
  const recentNews = dashboardData?.recent_news || [];
  const mostViewedStocks = dashboardData?.most_viewed || [];

  // Find the selected index data
  const selectedIndexData = marketOverviewData.indices?.find(index => 
    index.name === selectedIndex
  ) || null;
  
  // Prepare top movers data from market overview
  const topGainers = marketOverviewData.top_gainers || [];
  const topLosers = marketOverviewData.top_losers || [];
  
  // Prepare movers data based on active tab
  let moversData = [];
  if (activeMoversTab === 'gainers') {
    moversData = topGainers;
  } else if (activeMoversTab === 'losers') {
    moversData = topLosers;
  } else if (activeMoversTab === 'volume') {
    // If you don't have volume data, use a placeholder
    moversData = [1, 2, 3, 4, 5].map(index => ({
      symbol: `VOL${index}`,
      name: `Volume Leader ${index}`,
      change_percent: 0,
      volume: Math.floor(Math.random() * 10000000)
    }));
  }
  
  // Prepare recent activity from most viewed
  const recentActivity = mostViewedStocks.slice(0, 3).map((stock, index) => ({
    stock: stock.symbol,
    action: 'Viewed details',
    time: index === 0 ? '5m ago' : index === 1 ? '22m ago' : '1h ago',
    type: 'view'
  }));
  
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-title-section">
          <h1>Market Dashboard</h1>
          <div className="dashboard-date">{formatDate(currentTime)}</div>
        </div>
        
        {useMockData && (
          <div className="mock-data-notice">
            <i className="notice-icon">ℹ️</i>
            <span>Using demonstration data - API connection unavailable</span>
          </div>
        )}
        
        <div className="market-status">
          <div className={`market-indicator ${isMarketOpen() ? 'online' : 'offline'}`}></div>
          <span className="status-text">{isMarketOpen() ? 'Market Open' : 'Market Closed'}</span>
          <span className="market-time">{formatTime(currentTime)}</span>
        </div>
      </div>
      
      <div className="dashboard-grid">
        {/* Main content column - rearranged order as requested */}
        <div className="dashboard-column main-column">
          {/* Watchlist moved to top */}
          <WatchlistWidget watchlists={userWatchlists} />
          
          {/* New Portfolio widget added below watchlist */}
          <PortfolioWidget portfolios={userPortfolios} />
          
          {/* Index and Market overview moved below */}
          <IndexPerformanceWidget indexData={selectedIndexData} />
          <MarketOverviewWidget marketData={marketOverviewData} />
        </div>
        
        {/* Side column remains with other widgets */}
        <div className="dashboard-column side-column">
          <StockNewsWidget news={recentNews} />
          <TechnicalAnalysisWidget />
        </div>
      </div>
      
      {/* Index selector moved below the main widgets */}
      <div className="index-selector-container">
        <div className="section-header">
          <h2>Market Indices</h2>
          <div className="section-actions">
            <button className="btn btn-text">View All Indices</button>
          </div>
        </div>
        
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
              className={`index-btn ${selectedIndex === index ? 'active' : ''}`}
              onClick={() => setSelectedIndex(index)}
            >
              {index.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>
      
      <div className="top-movers">
        <div className="section-header">
          <h2>Top Movers</h2>
          <div className="section-actions">
            <button className="btn btn-text">View All</button>
          </div>
        </div>
        
        <div className="movers-tabs">
          <button 
            className={`tab-btn ${activeMoversTab === 'gainers' ? 'active' : ''}`}
            onClick={() => setActiveMoversTab('gainers')}
          >
            Gainers
          </button>
          <button 
            className={`tab-btn ${activeMoversTab === 'losers' ? 'active' : ''}`}
            onClick={() => setActiveMoversTab('losers')}
          >
            Losers
          </button>
          <button 
            className={`tab-btn ${activeMoversTab === 'volume' ? 'active' : ''}`}
            onClick={() => setActiveMoversTab('volume')}
          >
            Volume
          </button>
        </div>
        
        <div className="movers-list">
          {(moversData.length > 0 ? moversData : [1, 2, 3, 4, 5].map(index => ({
            symbol: `STOCK${index}`,
            name: `Company Name ${index}`,
            change_percent: activeMoversTab === 'losers' ? -(Math.random() * 5) : (Math.random() * 5),
            volume: Math.floor(Math.random() * 1000000)
          }))).map((stock, index) => (
            <Link to={`/stock/${stock.symbol}`} key={index} className="mover-card">
              <div className="mover-info">
                <div className="mover-symbol">{stock.symbol}</div>
                <div className="mover-name">{stock.name}</div>
              </div>
              
              {activeMoversTab === 'volume' ? (
                <div className="mover-volume">{(stock.volume || 0).toLocaleString()} ₺</div>
              ) : (
                <div className={`mover-change ${stock.change_percent >= 0 ? 'positive' : 'negative'}`}>
                  {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                </div>
              )}
            </Link>
          ))}
        </div>
      </div>
      
      <div className="recent-activity">
        <div className="section-header">
          <h2>Recent Activity</h2>
          <div className="section-actions">
            <button className="btn btn-text">View All</button>
          </div>
        </div>
        
        <div className="activity-list">
          {recentActivity.length > 0 ? (
            recentActivity.map((activity, index) => (
              <div className="activity-item" key={index}>
                <div className={`activity-icon ${activity.type}`}></div>
                <div className="activity-details">
                  <span className="activity-stock">{activity.stock}</span>
                  <span className="activity-action">{activity.action}</span>
                </div>
                <div className="activity-time">{activity.time}</div>
              </div>
            ))
          ) : (
            <div className="empty-activity">
              <div className="empty-icon">📋</div>
              <p>No recent activity</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;