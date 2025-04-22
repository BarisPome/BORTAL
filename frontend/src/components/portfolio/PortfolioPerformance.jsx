import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import PortfolioService from '../../services/PortfolioService';
import '../../styles/components/portfolio/PortfolioPerformance.css';

export default function PortfolioPerformance({ portfolioId }) {
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeFrame, setTimeFrame] = useState('1m');

  useEffect(() => {
    if (!portfolioId) return;
    fetchPerformanceData();
  }, [portfolioId]);

  const fetchPerformanceData = async () => {
    setLoading(true);
    try {
      const res = await PortfolioService.getPerformance(portfolioId);
      setPerformanceData(res.data.data);
    } catch (err) {
      console.error('Failed to fetch performance data:', err);
      setError('Performans verileri yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const getTimeFrameData = () => {
    if (!performanceData || !performanceData.daily_values) return [];
    
    let filteredData = [];
    const now = new Date();
    
    switch (timeFrame) {
      case '1w':
        // Last 7 days
        const oneWeekAgo = new Date(now);
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
        filteredData = performanceData.daily_values.filter(
          item => new Date(item.date) >= oneWeekAgo
        );
        break;
      case '1m':
        // Last 30 days
        const oneMonthAgo = new Date(now);
        oneMonthAgo.setDate(oneMonthAgo.getDate() - 30);
        filteredData = performanceData.daily_values.filter(
          item => new Date(item.date) >= oneMonthAgo
        );
        break;
      case '3m':
        // Last 90 days
        const threeMonthsAgo = new Date(now);
        threeMonthsAgo.setDate(threeMonthsAgo.getDate() - 90);
        filteredData = performanceData.daily_values.filter(
          item => new Date(item.date) >= threeMonthsAgo
        );
        break;
      case '1y':
        // Last 365 days
        const oneYearAgo = new Date(now);
        oneYearAgo.setDate(oneYearAgo.getDate() - 365);
        filteredData = performanceData.daily_values.filter(
          item => new Date(item.date) >= oneYearAgo
        );
        break;
      case 'all':
      default:
        filteredData = performanceData.daily_values;
        break;
    }
    
    return filteredData.map(item => ({
      ...item,
      date: new Date(item.date).toLocaleDateString('tr-TR'),
    }));
  };

  const formatCurrency = (value) => {
    return `${value.toLocaleString('tr-TR')} ₺`;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="performance-tooltip">
          <p className="tooltip-date">{label}</p>
          <p className="tooltip-value">
            <span className="tooltip-label">Değer:</span> {formatCurrency(payload[0].value)}
          </p>
          {payload[1] && (
            <p className="tooltip-cost">
              <span className="tooltip-label">Maliyet:</span> {formatCurrency(payload[1].value)}
            </p>
          )}
          {payload[0].payload.daily_return_percent !== undefined && (
            <p className={`tooltip-return ${payload[0].payload.daily_return_percent >= 0 ? 'positive' : 'negative'}`}>
              <span className="tooltip-label">Günlük Değişim:</span> {payload[0].payload.daily_return_percent.toFixed(2)}%
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return <div className="performance-loading">Performans verileri yükleniyor...</div>;
  }

  if (error) {
    return (
      <div className="performance-error">
        <p>{error}</p>
        <button onClick={fetchPerformanceData}>Yeniden Dene</button>
      </div>
    );
  }

  if (!performanceData || !performanceData.daily_values || performanceData.daily_values.length === 0) {
    return (
      <div className="performance-empty">
        <p>Henüz yeterli performans verisi bulunmamaktadır.</p>
        <p>İşlemler yaptıkça portföy performansınız burada görüntülenecektir.</p>
      </div>
    );
  }

  const chartData = getTimeFrameData();
  const totalReturn = performanceData.overall_return_percent;
  const returnColor = totalReturn >= 0 ? 'positive' : 'negative';

  return (
    <div className="portfolio-performance">
      <div className="performance-header">
        <h3>Portföy Performansı</h3>
        <div className="time-frame-selector">
          <button 
            className={timeFrame === '1w' ? 'active' : ''} 
            onClick={() => setTimeFrame('1w')}
          >
            1H
          </button>
          <button 
            className={timeFrame === '1m' ? 'active' : ''} 
            onClick={() => setTimeFrame('1m')}
          >
            1A
          </button>
          <button 
            className={timeFrame === '3m' ? 'active' : ''} 
            onClick={() => setTimeFrame('3m')}
          >
            3A
          </button>
          <button 
            className={timeFrame === '1y' ? 'active' : ''} 
            onClick={() => setTimeFrame('1y')}
          >
            1Y
          </button>
          <button 
            className={timeFrame === 'all' ? 'active' : ''} 
            onClick={() => setTimeFrame('all')}
          >
            Tümü
          </button>
        </div>
      </div>

      <div className="performance-metrics">
        <div className="metric">
          <span className="metric-label">Toplam Getiri:</span>
          <span className={`metric-value ${returnColor}`}>
            {totalReturn.toFixed(2)}%
          </span>
        </div>
        {performanceData.annual_return_percent !== undefined && (
          <div className="metric">
            <span className="metric-label">Yıllık Getiri:</span>
            <span className={`metric-value ${performanceData.annual_return_percent >= 0 ? 'positive' : 'negative'}`}>
              {performanceData.annual_return_percent.toFixed(2)}%
            </span>
          </div>
        )}
        {performanceData.max_drawdown_percent !== undefined && (
          <div className="metric">
            <span className="metric-label">Maksimum Düşüş:</span>
            <span className="metric-value negative">
              {performanceData.max_drawdown_percent.toFixed(2)}%
            </span>
          </div>
        )}
      </div>

      <div className="performance-chart">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date"
              tickMargin={10}
              minTickGap={30}
            />
            <YAxis 
              yAxisId="left"
              orientation="left"
              tickFormatter={(value) => `${value.toLocaleString('tr-TR')} ₺`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="value" 
              name="Portföy Değeri"
              stroke="#2E7D32" 
              activeDot={{ r: 8 }} 
              dot={false}
              strokeWidth={2}
            />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="cost_basis" 
              name="Maliyet"
              stroke="#757575" 
              dot={false}
              strokeDasharray="5 5"
              strokeWidth={1.5}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {performanceData.holdings_performance && performanceData.holdings_performance.length > 0 && (
        <div className="holdings-performance">
          <h4>Hisse Senetleri Performansı</h4>
          <div className="holdings-table-container">
            <table className="holdings-performance-table">
              <thead>
                <tr>
                  <th>Sembol</th>
                  <th>Alokasyon</th>
                  <th>Getiri</th>
                  <th>Katkı</th>
                </tr>
              </thead>
              <tbody>
                {performanceData.holdings_performance.map((holding) => (
                  <tr key={holding.symbol}>
                    <td className="symbol-cell">{holding.symbol}</td>
                    <td>{holding.allocation_percent.toFixed(2)}%</td>
                    <td className={`${holding.return_percent >= 0 ? 'positive' : 'negative'}`}>
                      {holding.return_percent.toFixed(2)}%
                    </td>
                    <td className={`${holding.contribution_percent >= 0 ? 'positive' : 'negative'}`}>
                      {holding.contribution_percent.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}