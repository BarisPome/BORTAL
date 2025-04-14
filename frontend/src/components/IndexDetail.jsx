import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

function IndexDetail() {
  const [index, setIndex] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { name } = useParams();

  useEffect(() => {
    axios.get(`${API_BASE_URL}/indices/${name}/`)
      .then(response => {
        setIndex(response.data);
        setLoading(false);
      })
      .catch(error => {
        setError(`Error fetching stocks for ${name}`);
        setLoading(false);
        console.error('Error fetching stocks:', error);
      });
  }, [name]);

  if (loading) return <div className="loading">Loading stocks...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!index) return <div>Index not found</div>;

  return (
    <div className="index-detail-container">
      <div className="header">
        <h1>{index.name} Stocks</h1>
        <Link to="/" className="back-link">Back to Indices</Link>
      </div>
      
      <div className="stocks-table-container">
        <table className="stocks-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th>Indices</th>
            </tr>
          </thead>
          <tbody>
            {index.stocks.map(stock => (
              <tr key={stock.id}>
                <td>{stock.symbol}</td>
                <td>{stock.name}</td>
                <td>
                  {stock.indices.map((idx, i) => (
                    <span key={i} className="index-tag">
                      {idx}
                      {i < stock.indices.length - 1 ? ', ' : ''}
                    </span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default IndexDetail;