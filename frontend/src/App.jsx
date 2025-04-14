import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import IndexList from './pages/IndexList';
import IndexDetail from './pages/IndexDetail';
import StockDetail from './pages/StockDetail';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/indices" element={<IndexList />} />
          <Route path="/index/:name" element={<IndexDetail />} />
          <Route path="/stock/:symbol" element={<StockDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;