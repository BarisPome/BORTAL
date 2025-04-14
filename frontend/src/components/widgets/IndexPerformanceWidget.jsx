// src/components/widgets/IndexPerformanceWidget.jsx
import { useState, useEffect } from 'react';
import '../../styles/components/widgets/index-performance-widget.css';

function IndexPerformanceWidget({ indexName }) {
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Mock data loading
    setLoading(true);
    setTimeout(() => {
      setPerformance({
        value: 9875.32,
        change: 125.68,
        percentChange: 1.29,
        volume: 5234000000,
        positive: true
      });
      setLoading(false);
    }, 800);
  }, [indexName]);
  
  if (loading) return <div className="widget index-performance-widget loading">Loading...</div>;
  
  return (
    <div className="widget index-performance-widget">
      <div className="widget-header">
        <h3>{indexName}</h3>
        <div className="widget-controls">
          <button className="widget-control">
            <span className="control-icon refresh"></span>
          </button>
          <button className="widget-control">
            <span className="control-icon expand"></span>
          </button>
        </div>
      </div>
      
      <div className="index-summary">
        <div className="index-value">{performance.value.toLocaleString()}</div>
        <div className={`index-change ${performance.positive ? 'positive' : 'negative'}`}>
          {performance.positive ? '+' : ''}{performance.change.toFixed(2)} ({performance.percentChange.toFixed(2)}%)
        </div>
      </div>
      
      <div className="index-chart">
        {/* Chart would go here */}
        <div className="chart-placeholder"></div>
      </div>
      
      <div className="index-metrics">
        <div className="metric">
          <span className="metric-label">Volume</span>
          <span className="metric-value">{(performance.volume / 1000000).toFixed(2)}M</span>
        </div>
        <div className="metric">
          <span className="metric-label">Open</span>
          <span className="metric-value">{(performance.value - 25).toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">High</span>
          <span className="metric-value">{(performance.value + 15).toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Low</span>
          <span className="metric-value">{(performance.value - 45).toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}

export default IndexPerformanceWidget;