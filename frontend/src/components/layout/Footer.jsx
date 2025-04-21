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
            <h3 className="footer-section-title">Quick Links</h3>
            <ul className="footer-nav">
              <li><Link to="/">Dashboard</Link></li>
              <li><Link to="/market">Market</Link></li>
              <li><Link to="/watchlists">Watchlists</Link></li>
              <li><Link to="/portfolios">Portfolios</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h3 className="footer-section-title">Resources</h3>
            <ul className="footer-nav">
              <li><Link to="/help">Help Center</Link></li>
              <li><Link to="/faq">FAQ</Link></li>
              <li><Link to="/contact">Contact</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h3 className="footer-section-title">Legal</h3>
            <ul className="footer-nav">
              <li><Link to="/terms">Terms of Service</Link></li>
              <li><Link to="/privacy">Privacy Policy</Link></li>
              <li><Link to="/disclaimer">Disclaimer</Link></li>
            </ul>
          </div>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p className="copyright">
          &copy; {currentYear} BORTAL. All rights reserved.
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