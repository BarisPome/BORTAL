// src/services/stockService.js
import api from './api';

export const getStocks = async (indexName = null) => {
  const params = indexName ? { index: indexName } : {};
  const response = await api.get('/stocks/', { params });
  return response.data;
};

export const getStockDetail = async (symbol) => {
  const response = await api.get(`/stocks/${symbol}/detail/`);
  return response.data;
};