// src/context/AuthContext.jsx
import React, { createContext, useState, useEffect, useContext } from 'react';
import { isAuthenticated, getUser, login, register, logout, getUserProfile } from '../services/authService';

// Create the Auth Context
const AuthContext = createContext();

// Auth Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Initialize authentication state on component mount
  useEffect(() => {
    const initAuth = async () => {
      setLoading(true);
      
      try {
        if (isAuthenticated()) {
          // Get user from localStorage first for quick loading
          const storedUser = getUser();
          if (storedUser) {
            setUser(storedUser);
          }
          
          // Then fetch the latest user profile from API
          try {
            const profile = await getUserProfile();
            setUser(profile);
            localStorage.setItem('user', JSON.stringify(profile));
          } catch (profileError) {
            console.error('Error fetching user profile:', profileError);
            // If profile fetch fails but token exists, keep using stored user
          }
        } else {
          setUser(null);
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
        setError(err.message);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    
    initAuth();
  }, []);
  
  // Login handler
  const handleLogin = async (username, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const user = await login(username, password);
      setUser(user);
      return user;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Login failed. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  // Register handler
  const handleRegister = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      const user = await register(userData);
      setUser(user);
      return user;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Registration failed. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  // Logout handler
  const handleLogout = async () => {
    setLoading(true);
    
    try {
      await logout();
      setUser(null);
      return true;
    } catch (err) {
      console.error('Logout error:', err);
      // Even if logout API fails, clear user from state
      setUser(null);
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  // Values provided to context consumers
  const authContextValue = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout
  };
  
  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export default AuthContext;