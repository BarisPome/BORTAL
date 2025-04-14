// src/pages/IndexList.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getIndices } from '../services/indexService';
import '../styles/components/index-list.css';

function IndexList() {
  const [indices, setIndices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchIndices = async () => {
      try {
        const data = await getIndices();
        setIndices(data);
        setLoading(false);
      } catch (error) {
        setError('Error fetching indices');
        setLoading(false);
        console.error('Error fetching indices:', error);
      }
    };

    fetchIndices();
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