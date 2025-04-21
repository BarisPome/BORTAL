// src/components/layout/Header.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import '../../styles/components/layout/header.css';

function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/auth/login');
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-brand">
          <Link to="/" className="logo">BORTAL</Link>
          <div className="logo-subtitle">Borsa Portalı</div>
        </div>

        <nav className="main-nav">
          <ul className="nav-list desktop-nav">
            <li className="nav-item"><Link to="/" className="nav-link">Anasayfa</Link></li>
            <li className="nav-item"><Link to="/market" className="nav-link">Piyasa</Link></li>
            <li className="nav-item"><Link to="/watchlists" className="nav-link">İzleme Listeleri</Link></li>
            <li className="nav-item"><Link to="/portfolios" className="nav-link">Portföyler</Link></li>
          </ul>
        </nav>

        <div className="header-actions">
          {isAuthenticated ? (
            <div className="user-menu">
              <button className="user-menu-button" onClick={toggleMenu}>
                <div className="user-avatar">
                  {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                </div>
                <span className="user-name">{user?.first_name || user?.username}</span>
                <span className="dropdown-icon">▼</span>
              </button>

              {isMenuOpen && (
                <div className="dropdown-menu">
                  <Link to="/profile" className="dropdown-item">Profilim</Link>
                  <Link to="/settings" className="dropdown-item">Ayarlar</Link>
                  <hr className="dropdown-divider" />
                  <button onClick={handleLogout} className="dropdown-item logout">Çıkış Yap</button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-buttons">
              <Link to="/auth/login" className="btn btn-text">Giriş Yap</Link>
              <Link to="/auth/register" className="btn btn-primary">Kayıt Ol</Link>
            </div>
          )}

          <button className="mobile-menu-toggle" onClick={toggleMenu}>
            <span className="hamburger"></span>
          </button>
        </div>
      </div>

      {isMenuOpen && (
        <div className="mobile-menu">
          <ul className="nav-list">
            <li className="nav-item"><Link to="/" className="nav-link" onClick={() => setIsMenuOpen(false)}>Anasayfa</Link></li>
            <li className="nav-item"><Link to="/market" className="nav-link" onClick={() => setIsMenuOpen(false)}>Piyasa</Link></li>
            <li className="nav-item"><Link to="/watchlists" className="nav-link" onClick={() => setIsMenuOpen(false)}>İzleme Listeleri</Link></li>
            <li className="nav-item"><Link to="/portfolios" className="nav-link" onClick={() => setIsMenuOpen(false)}>Portföyler</Link></li>
            {isAuthenticated && (
              <>
                <li className="nav-item"><Link to="/profile" className="nav-link" onClick={() => setIsMenuOpen(false)}>Profilim</Link></li>
                <li className="nav-item"><Link to="/settings" className="nav-link" onClick={() => setIsMenuOpen(false)}>Ayarlar</Link></li>
                <li className="nav-item"><button onClick={handleLogout} className="nav-link logout-link">Çıkış Yap</button></li>
              </>
            )}
          </ul>
        </div>
      )}
    </header>
  );
}

export default Header;
