import api from './apiClient';

/**
 * Fetch a list of stocks, optionally filtered by index name.
 * Returns an array of stock objects.
 *
 * @param {string|null} indexName - Optional index name to filter stocks.
 * @returns {Promise<Array>} List of stocks
 */
export const getStocks = async (indexName = null) => {
  const params = indexName ? { index: indexName } : {};
  const { data } = await api.get('/stocks/', { params });
  // unwrap the inner `data` payload from our BaseAPIView
  return data.data;
};

/**
 * Fetch detailed information for a single stock symbol.
 * Returns a stock detail object containing latest_price, fundamentals, price_history, etc.
 *
 * @param {string} symbol - The stock symbol to fetch
 * @param {string} range - Time range for price history (e.g. '1m', '1y')
 * @returns {Promise<Object>} Stock detail
 */
export const getStockDetail = async (symbol, range = '1m') => {
  const { data } = await api.get(`/stocks/${symbol}/`, {
    params: { range }
  });
  // unwrap the inner `data` payload
  return data.data;
};