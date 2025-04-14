import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

function IndexList() {
  const [indices, setIndices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/indices/`)
      .then(response => {
        setIndices(response.data);
        setLoading(false);
      })
      .catch(error => {
        setError('Error fetching indices');
        setLoading(false);
        console.error('Error fetching indices:', error);
      });
  }, []);

  if (loading) return <div className="loading">Loading indices...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="index-list-container">
      <h1>Stock Indices</h1>
      <div className="index-list">
        {indices.map(index => (
          <div key={index.id} className="index-card">
            <Link to={`/index/${index.name}`}>
              <h2>{index.name}</h2>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

export default IndexList;