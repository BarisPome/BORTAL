// src/pages/IndexDetail.jsx
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getIndexDetail } from '../services/indexService';
import '../styles/components/index-detail.css';
import '../styles/components/ui-elements.css';

function IndexDetail() {
  const [index, setIndex] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const { name } = useParams();

  useEffect(() => {
    const fetchIndexDetail = async () => {
      try {
        const data = await getIndexDetail(name);
        setIndex(data);
        setLoading(false);
      } catch (error) {
        setError(`Error fetching stocks for ${name}`);
        setLoading(false);
        console.error('Error fetching stocks:', error);
      }
    };

    fetchIndexDetail();
  }, [name]);

  if (loading) return <div className="loading">Loading stocks...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!index) return <div>Index not found</div>;

  const filteredStocks = index.stocks.filter(stock => 
    stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) || 
    stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="index-detail-container">
      <div className="header">
        <h1>{index.name} Stocks</h1>
        <Link to="/" className="back-link">Back to Indices</Link>
      </div>
      
      <div className="filters-container">
        <div className="search-container">
          <input
            type="text"
            placeholder="Search by symbol or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="stats">
          <span>Total: {filteredStocks.length} stocks</span>
        </div>
      </div>
      
      <div className="stocks-table-container">
        <table className="stocks-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th>Indices</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredStocks.map(stock => (
              <tr key={stock.id}>
                <td>
                  <strong>{stock.symbol}</strong>
                </td>
                <td>{stock.name}</td>
                <td>
                  {stock.indices.map((idx, i) => (
                    <Link 
                      key={i} 
                      to={`/index/${idx}`} 
                      className="index-badge"
                    >
                      {idx}
                    </Link>
                  ))}
                </td>
                <td>
                  <Link to={`/stock/${stock.symbol}`} className="view-button">
                    View Details
                  </Link>
                </td>
              </tr>
            ))}
            {filteredStocks.length === 0 && (
              <tr>
                <td colSpan="4" className="no-results">
                  No stocks found matching "{searchTerm}"
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default IndexDetail;