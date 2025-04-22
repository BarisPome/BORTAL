import api from './apiClient';

const PortfolioService = {
  getPortfolios: () => api.get('/portfolios/'),

  getPortfolioDetail: (id) => api.get(`/portfolios/${id}/`),

  createPortfolio: (data) => api.post('/portfolios/', data),

  deletePortfolio: (id) => api.delete(`/portfolios/${id}/`),

  getTransactions: (portfolioId, params = {}) =>
    api.get(`/portfolios/${portfolioId}/transactions/`, { params }),

  createTransaction: (portfolioId, data) =>
    api.post(`/portfolios/${portfolioId}/transactions/`, data),

  deleteTransaction: (portfolioId, transactionId) =>
    api.delete(`/portfolios/${portfolioId}/transactions/${transactionId}/`),

  getPerformance: (portfolioId) =>
    api.get(`/portfolios/${portfolioId}/performance/`)
};

export default PortfolioService;
