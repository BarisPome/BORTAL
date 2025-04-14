// src/services/indexService.js
import api from './api';

export const getIndices = async () => {
  const response = await api.get('/indices/');
  return response.data;
};

export const getIndexDetail = async (name) => {
  const response = await api.get(`/indices/${name}/`);
  return response.data;
};