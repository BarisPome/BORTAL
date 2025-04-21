// src/components/layout/Footer.jsx
import { Link } from 'react-router-dom';
import '../../styles/components/layout/footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-brand">
          <div className="footer-logo">BORTAL</div>
          <p className="footer-tagline">
            Türkiye'nin öncü borsa portalı
          </p>
        </div>
        
        <div className="footer-links">
          <div className="footer-section">
            <h3 className="footer-section-title">Hızlı Erişim</h3>
            <ul className="footer-nav">
              <li><Link to="/">Gösterge Paneli</Link></li>
              <li><Link to="/market">Piyasa</Link></li>
              <li><Link to="/watchlists">İzleme Listeleri</Link></li>
              <li><Link to="/portfolios">Portföyler</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h3 className="footer-section-title">Kaynaklar</h3>
            <ul className="footer-nav">
              <li><Link to="/help">Yardım Merkezi</Link></li>
              <li><Link to="/faq">SSS</Link></li>
              <li><Link to="/contact">İletişim</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h3 className="footer-section-title">Yasal</h3>
            <ul className="footer-nav">
              <li><Link to="/terms">Hizmet Şartları</Link></li>
              <li><Link to="/privacy">Gizlilik Politikası</Link></li>
              <li><Link to="/disclaimer">Yasal Uyarı</Link></li>
            </ul>
          </div>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p className="copyright">
          &copy; {currentYear} BORTAL. Tüm hakları saklıdır.
        </p>
        <div className="footer-social">
          <a href="#" className="social-link">
            <i className="social-icon twitter"></i>
          </a>
          <a href="#" className="social-link">
            <i className="social-icon facebook"></i>
          </a>
          <a href="#" className="social-link">
            <i className="social-icon instagram"></i>
          </a>
          <a href="#" className="social-link">
            <i className="social-icon linkedin"></i>
          </a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
