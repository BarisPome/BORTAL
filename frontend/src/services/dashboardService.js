// src/services/dashboardService.js
import api from './apiClient';

/**
 * Fetch dashboard data from the API
 * @returns {Promise} Promise with the dashboard data
 */
export const getDashboardData = () => {
  // Try with both URL patterns since we're not sure which one your Django is using
  return api.get('dashboard/');
};

/**
 * Get a specific index data
 * @param {string} indexName - The name of the index to fetch
 * @returns {Promise} Promise with the index data
 */
export const getIndexData = (indexName) => {
  return api.get(`/indices/${indexName}/`);
};

/**
 * Get user's watchlists
 * @returns {Promise} Promise with the user's watchlists
 */
export const getUserWatchlists = () => {
  return api.get('/watchlists/');
};

/**
 * Get user's portfolios
 * @returns {Promise} Promise with the user's portfolios
 */
export const getUserPortfolios = () => {
  return api.get('/portfolios/');
};

/**
 * Get recent news
 * @param {number} limit - The number of news items to fetch
 * @returns {Promise} Promise with the news data
 */
export const getRecentNews = (limit = 10) => {
  return api.get(`/news/?limit=${limit}`);
};

/**
 * Get most viewed stocks
 * @param {number} limit - The number of stocks to fetch
 * @returns {Promise} Promise with the stocks data
 */
export const getMostViewedStocks = (limit = 10) => {
  return api.get(`/stocks/most-viewed/?limit=${limit}`);
};