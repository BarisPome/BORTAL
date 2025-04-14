// src/components/widgets/MarketOverviewWidget.jsx
import { useState, useEffect } from 'react';
import '../../styles/components/widgets/market-overview-widget.css';

function MarketOverviewWidget() {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Mock data loading - replace with actual API call
    setLoading(true);
    setTimeout(() => {
      setMarketData({
        sectors: [
          { name: 'Banking', change: 2.34, volume: 123000000, value: 352000000 },
          { name: 'Technology', change: 1.75, volume: 87000000, value: 215000000 },
          { name: 'Energy', change: -0.82, volume: 98000000, value: 178000000 },
          { name: 'Industrials', change: 0.46, volume: 76000000, value: 164000000 },
          { name: 'Materials', change: -1.23, volume: 68000000, value: 142000000 },
          { name: 'Consumer', change: 0.91, volume: 54000000, value: 128000000 },
        ]
      });
      setLoading(false);
    }, 1000);
  }, []);
  
  if (loading) return <div className="widget market-overview-widget loading">Loading sectors...</div>;
  
  return (
    <div className="widget market-overview-widget">
      <div className="widget-header">
        <h3>Market Overview</h3>
        <div className="widget-controls">
          <button className="widget-control">
            <span className="control-icon refresh"></span>
          </button>
          <button className="widget-control">
            <span className="control-icon expand"></span>
          </button>
        </div>
      </div>
      
      <div className="market-heatmap">
        <div className="heatmap-header">
          <span className="sector-title">Sector</span>
          <span className="sector-change">Change</span>
          <span className="sector-volume">Volume</span>
        </div>
        
        <div className="heatmap-body">
          {marketData.sectors.map((sector, index) => (
            <div 
              key={index} 
              className="sector-row"
              style={{
                background: `linear-gradient(to right, 
                  ${sector.change > 0 
                    ? 'rgba(46, 204, 113, 0.2)' 
                    : 'rgba(231, 76, 60, 0.2)'} 
                  ${Math.min(Math.abs(sector.change) * 10, 100)}%, 
                  transparent 100%)`
              }}
            >
              <span className="sector-title">{sector.name}</span>
              <span className={`sector-change ${sector.change > 0 ? 'positive' : 'negative'}`}>
                {sector.change > 0 ? '+' : ''}{sector.change.toFixed(2)}%
              </span>
              <span className="sector-volume">
                {(sector.volume / 1000000).toFixed(1)}M
              </span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="market-summary">
        <div className="summary-stat">
          <span className="stat-label">Top Sector</span>
          <span className="stat-value">Banking (+2.34%)</span>
        </div>
        <div className="summary-stat">
          <span className="stat-label">Total Volume</span>
          <span className="stat-value">506M</span>
        </div>
        <div className="summary-stat">
          <span className="stat-label">Market Value</span>
          <span className="stat-value">1.18T</span>
        </div>
      </div>
    </div>
  );
}

export default MarketOverviewWidget;