// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import IndexList from './pages/IndexList';
import IndexDetail from './pages/IndexDetail';
import StockDetail from './pages/StockDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<IndexList />} />
          <Route path="/index/:name" element={<IndexDetail />} />
          <Route path="/stock/:symbol" element={<StockDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;