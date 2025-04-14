// src/components/widgets/TechnicalAnalysisWidget.jsx
import { useState } from 'react';
import '../../styles/components/widgets/technical-analysis-widget.css';

function TechnicalAnalysisWidget() {
  const [activeTab, setActiveTab] = useState('summary');
  const [selectedStock, setSelectedStock] = useState('THYAO');
  
  const technicalData = {
    THYAO: {
      summary: {
        signal: 'BUY',
        oscillators: 'NEUTRAL',
        movingAverages: 'BUY',
        strength: 7,
      },
      indicators: [
        { name: 'RSI (14)', value: 58.43, signal: 'NEUTRAL' },
        { name: 'MACD (12,26)', value: 1.25, signal: 'BUY' },
        { name: 'Stochastic (14,3,3)', value: 72.15, signal: 'NEUTRAL' },
        { name: 'CCI (14)', value: 112.53, signal: 'BUY' },
        { name: 'ATR (14)', value: 3.42, signal: 'NEUTRAL' },
      ],
      movingAverages: [
        { name: 'MA 5', value: 53.42, signal: 'BUY' },
        { name: 'MA 10', value: 52.18, signal: 'BUY' },
        { name: 'MA 20', value: 51.27, signal: 'BUY' },
        { name: 'MA 50', value: 48.92, signal: 'BUY' },
        { name: 'MA 100', value: 45.63, signal: 'BUY' },
        { name: 'MA 200', value: 42.85, signal: 'BUY' },
      ]
    },
    AKBNK: {
      summary: {
        signal: 'NEUTRAL',
        oscillators: 'SELL',
        movingAverages: 'BUY',
        strength: 5,
      },
      indicators: [
        { name: 'RSI (14)', value: 42.18, signal: 'NEUTRAL' },
        { name: 'MACD (12,26)', value: -0.32, signal: 'SELL' },
        { name: 'Stochastic (14,3,3)', value: 28.75, signal: 'SELL' },
        { name: 'CCI (14)', value: -85.37, signal: 'SELL' },
        { name: 'ATR (14)', value: 1.15, signal: 'NEUTRAL' },
      ],
      movingAverages: [
        { name: 'MA 5', value: 22.85, signal: 'BUY' },
        { name: 'MA 10', value: 22.42, signal: 'BUY' },
        { name: 'MA 20', value: 21.95, signal: 'BUY' },
        { name: 'MA 50', value: 21.23, signal: 'BUY' },
        { name: 'MA 100', value: 20.18, signal: 'BUY' },
        { name: 'MA 200', value: 19.75, signal: 'BUY' },
      ]
    }
  };
  
  const stocks = [
    { symbol: 'THYAO', name: 'Turkish Airlines' },
    { symbol: 'AKBNK', name: 'Akbank' }
  ];
  
  const data = technicalData[selectedStock];
  
  const renderSignalIndicator = (signal) => {
    let colorClass = '';
    switch(signal) {
      case 'BUY':
        colorClass = 'positive';
        break;
      case 'SELL':
        colorClass = 'negative';
        break;
      default:
        colorClass = 'neutral';
    }
    
    return <span className={`signal-indicator ${colorClass}`}>{signal}</span>;
  };
  
  return (
    <div className="widget technical-analysis-widget">
      <div className="widget-header">
        <h3>Technical Analysis</h3>
        <div className="widget-controls">
          <button className="widget-control">
            <span className="control-icon expand"></span>
          </button>
        </div>
      </div>
      
      <div className="stock-selector">
        <select 
          value={selectedStock}
          onChange={(e) => setSelectedStock(e.target.value)}
        >
          {stocks.map(stock => (
            <option key={stock.symbol} value={stock.symbol}>
              {stock.symbol} - {stock.name}
            </option>
          ))}
        </select>
      </div>
      
      <div className="analysis-tabs">
        <button
          className={activeTab === 'summary' ? 'active' : ''}
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
        <button
          className={activeTab === 'oscillators' ? 'active' : ''}
          onClick={() => setActiveTab('oscillators')}
        >
          Oscillators
        </button>
        <button
          className={activeTab === 'movingAverages' ? 'active' : ''}
          onClick={() => setActiveTab('movingAverages')}
        >
          Moving Averages
        </button>
      </div>
      
      <div className="analysis-content">
        {activeTab === 'summary' && (
          <div className="summary-tab">
            <div className="signal-summary">
              <div className="signal-gauge">
                <div 
                  className="signal-value" 
                  style={{
                    transform: `rotate(${data.summary.strength * 18 - 90}deg)`
                  }}
                ></div>
                <div className="signal-display">
                  {renderSignalIndicator(data.summary.signal)}
                </div>
              </div>
            </div>
            
            <div className="summary-details">
              <div className="summary-item">
                <span className="summary-label">Moving Averages</span>
                {renderSignalIndicator(data.summary.movingAverages)}
              </div>
              <div className="summary-item">
                <span className="summary-label">Oscillators</span>
                {renderSignalIndicator(data.summary.oscillators)}
              </div>
              <div className="summary-item">
                <span className="summary-label">Signal Strength</span>
                <span className="summary-value">{data.summary.strength}/10</span>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'oscillators' && (
          <div className="indicators-tab">
            <div className="indicators-list">
              {data.indicators.map((indicator, index) => (
                <div key={index} className="indicator-item">
                  <span className="indicator-name">{indicator.name}</span>
                  <span className="indicator-value">{indicator.value}</span>
                  {renderSignalIndicator(indicator.signal)}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {activeTab === 'movingAverages' && (
          <div className="moving-averages-tab">
            <div className="indicators-list">
              {data.movingAverages.map((ma, index) => (
                <div key={index} className="indicator-item">
                  <span className="indicator-name">{ma.name}</span>
                  <span className="indicator-value">{ma.value}</span>
                  {renderSignalIndicator(ma.signal)}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div className="widget-footer">
        <button className="detailed-analysis-btn">View Detailed Analysis</button>
      </div>
    </div>
  );
}

export default TechnicalAnalysisWidget;