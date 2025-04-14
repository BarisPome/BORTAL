// src/components/widgets/StockNewsWidget.jsx
import { useState, useEffect } from 'react';
import '../../styles/components/widgets/stock-news-widget.css';

function StockNewsWidget() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Mock data loading - replace with actual API call
    setLoading(true);
    setTimeout(() => {
      setNews([
        {
          id: 1,
          title: 'Turkish Central Bank holds interest rates steady at 50%',
          source: 'Financial Times',
          time: '2h ago',
          relatedSymbols: ['GARAN', 'AKBNK', 'YKBNK'],
          imageUrl: '/api/placeholder/60/60'
        },
        {
          id: 2,
          title: 'SASA announces new production facility, expects 30% capacity increase',
          source: 'Bloomberg',
          time: '4h ago',
          relatedSymbols: ['SASA'],
          imageUrl: '/api/placeholder/60/60'
        },
        {
          id: 3,
          title: 'Turkish Airlines reports record passenger numbers for Q2',
          source: 'Reuters',
          time: '6h ago',
          relatedSymbols: ['THYAO'],
          imageUrl: '/api/placeholder/60/60'
        },
        {
          id: 4,
          title: 'Energy sector faces challenges amid global price fluctuations',
          source: 'Anadolu Agency',
          time: '8h ago',
          relatedSymbols: ['TUPRS', 'AKSEN'],
          imageUrl: '/api/placeholder/60/60'
        }
      ]);
      setLoading(false);
    }, 1200);
  }, []);
  
  if (loading) return <div className="widget stock-news-widget loading">Loading news...</div>;
  
  return (
    <div className="widget stock-news-widget">
      <div className="widget-header">
        <h3>Market News</h3>
        <div className="widget-controls">
          <button className="widget-control">
            <span className="control-icon filter"></span>
          </button>
          <button className="widget-control">
            <span className="control-icon expand"></span>
          </button>
        </div>
      </div>
      
      <div className="news-list">
        {news.map(item => (
          <div key={item.id} className="news-item">
            <div className="news-image">
              <img src={item.imageUrl} alt={item.title} />
            </div>
            <div className="news-content">
              <h4 className="news-title">{item.title}</h4>
              <div className="news-meta">
                <span className="news-source">{item.source}</span>
                <span className="news-time">{item.time}</span>
              </div>
              <div className="news-symbols">
                {item.relatedSymbols.map((symbol, index) => (
                  <span key={index} className="news-symbol">{symbol}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="widget-footer">
        <button className="view-all-btn">View All News</button>
      </div>
    </div>
  );
}

export default StockNewsWidget;