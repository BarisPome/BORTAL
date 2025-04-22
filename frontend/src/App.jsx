// src/App.jsx
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Dashboard from './pages/Dashboard';
import StockDetail from './pages/Stock/StockDetail';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import NotFound from './pages/NotFound';
import WatchlistDetail from './pages/WatchlistDetail';

// Layout components
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Header />
          <main className="main-content">
            <Routes>
              {/* Public routes */}
              <Route path="/auth/login" element={<Login />} />
              <Route path="/auth/register" element={<Register />} />
              
              {/* Protected routes */}
              <Route 
                path="/" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/stock/:symbol" 
                element={
                  <ProtectedRoute>
                    <StockDetail />
                  </ProtectedRoute>
                } 
              />

              <Route
                path="/watchlists/:id" 
                element={
                  <ProtectedRoute>
                    <WatchlistDetail />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/watchlists" 
                element={
                  <ProtectedRoute>
                    <WatchlistDetail />
                  </ProtectedRoute>
                }
              />



              
              {/* Not found route */}
              <Route path="/404" element={<NotFound />} />
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;