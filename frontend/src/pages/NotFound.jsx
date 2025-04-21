// src/pages/NotFound.jsx
import { Link } from 'react-router-dom';
import '../styles/pages/not-found.css';

function NotFound() {
  return (
    <div className="not-found">
      <div className="not-found-content">
        <div className="not-found-code">404</div>
        <h1 className="not-found-title">Page Not Found</h1>
        <p className="not-found-message">
          The page you are looking for does not exist or has been moved.
        </p>
        <div className="not-found-actions">
          <Link to="/" className="btn btn-primary">
            Go to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}

export default NotFound;