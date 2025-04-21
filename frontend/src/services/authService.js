// src/services/authService.js
import api from './apiClient';

// Store token in localStorage
const storeTokens = (tokens) => {
  localStorage.setItem('access_token', tokens.access);
  localStorage.setItem('refresh_token', tokens.refresh);
};

// Remove tokens from localStorage
const removeTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

// Store user in localStorage
const storeUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

// Get user from localStorage
export const getUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

// Login user
export const login = async (username, password) => {
  try {
    const response = await api.post('auth/login/', { username, password });
    const { user, tokens } = response.data;
    
    storeTokens(tokens);
    storeUser(user);
    
    return user;
  } catch (error) {
    throw error;
  }
};

// Register user
export const register = async (userData) => {
  try {
    const response = await api.post('auth/register/', userData);
    const { user, tokens } = response.data;
    
    storeTokens(tokens);
    storeUser(user);
    
    return user;
  } catch (error) {
    throw error;
  }
};

// Logout user
export const logout = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (refreshToken) {
      await api.post('auth/logout/', { refresh_token: refreshToken });
    }
    
    removeTokens();
    return true;
  } catch (error) {
    // Even if the API call fails, clear tokens
    removeTokens();
    throw error;
  }
};

// Refresh token
export const refreshToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response = await api.post('auth/token/refresh/', {
      refresh: refreshToken
    });
    
    localStorage.setItem('access_token', response.data.access);
    
    return response.data.access;
  } catch (error) {
    // If refresh fails, log the user out
    removeTokens();
    throw error;
  }
};

// Get user profile
export const getUserProfile = async () => {
  try {
    const response = await api.get('auth/profile/');
    return response.data;
  } catch (error) {
    throw error;
  }
};