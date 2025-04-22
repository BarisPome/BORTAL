import React, { useState, useEffect } from 'react';
import PortfolioService from '../../services/PortfolioService';

import '../../styles/components/portfolio/PortfolioTransactions.css';

export default function PortfolioTransactions({ portfolioId, onAddTransaction }) {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filter, setFilter] = useState({
    type: '',
    symbol: '',
    days: 30
  });

  useEffect(() => {
    fetchTransactions();
  }, [portfolioId, page, filter]);

  const fetchTransactions = async () => {
    if (!portfolioId) return;
    
    setLoading(true);
    try {
      const params = {
        page,
        page_size: 10,
        ...filter
      };
      
      const res = await PortfolioService.getTransactions(portfolioId, params);
      setTransactions(res.data.data);
      
      const totalCount = res.data.pagination.total_count;
      setTotalPages(Math.ceil(totalCount / 10));
    } catch (err) {
      setError('İşlem geçmişi yüklenemedi');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTransaction = async (transactionId) => {
    if (!confirm('Bu işlemi silmek istediğinize emin misiniz?')) return;
    
    try {
      await PortfolioService.deleteTransaction(portfolioId, transactionId);
      fetchTransactions();
    } catch (err) {
      alert('İşlem silinemedi');
      console.error(err);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilter(prev => ({ ...prev, [name]: value }));
    setPage(1); // Reset to first page when filter changes
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR') + ' ' + date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
  };

  const getTransactionTypeLabel = (type) => {
    switch (type) {
      case 'buy': return 'Alış';
      case 'sell': return 'Satış';
      case 'dividend': return 'Temettü';
      default: return type;
    }
  };

  const getTransactionTypeClass = (type) => {
    switch (type) {
      case 'buy': return 'transaction-buy';
      case 'sell': return 'transaction-sell';
      case 'dividend': return 'transaction-dividend';
      default: return '';
    }
  };

  return (
    <div className="portfolio-transactions">
      <div className="transactions-header">
        <h3>İşlem Geçmişi</h3>
        <button className="add-transaction-btn" onClick={onAddTransaction}>
          Yeni İşlem
        </button>
      </div>

      <div className="transactions-filter">
        <div className="filter-group">
          <label>İşlem Tipi</label>
          <select name="type" value={filter.type} onChange={handleFilterChange}>
            <option value="">Tümü</option>
            <option value="buy">Alış</option>
            <option value="sell">Satış</option>
            <option value="dividend">Temettü</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Hisse Senedi</label>
          <input 
            type="text" 
            name="symbol" 
            value={filter.symbol} 
            onChange={handleFilterChange}
            placeholder="HISSE"
          />
        </div>
        
        <div className="filter-group">
          <label>Süre</label>
          <select name="days" value={filter.days} onChange={handleFilterChange}>
            <option value="7">Son 7 gün</option>
            <option value="30">Son 30 gün</option>
            <option value="90">Son 90 gün</option>
            <option value="365">Son 1 yıl</option>
            <option value="">Tüm zamanlar</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="transactions-loading">Yükleniyor...</div>
      ) : error ? (
        <div className="transactions-error">{error}</div>
      ) : transactions.length === 0 ? (
        <div className="transactions-empty">
          <p>Henüz işlem bulunmuyor.</p>
        </div>
      ) : (
        <>
          <div className="transactions-table-container">
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>Tarih</th>
                  <th>İşlem</th>
                  <th>Hisse</th>
                  <th>Adet</th>
                  <th>Fiyat</th>
                  <th>Toplam</th>
                  <th>Notlar</th>
                  <th>İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td>{formatDate(transaction.transaction_date)}</td>
                    <td>
                      <span className={`transaction-type ${getTransactionTypeClass(transaction.transaction_type)}`}>
                        {getTransactionTypeLabel(transaction.transaction_type)}
                      </span>
                    </td>
                    <td className="symbol-cell">{transaction.stock.symbol}</td>
                    <td>{transaction.quantity}</td>
                    <td>{transaction.price_per_unit.toLocaleString('tr-TR')} ₺</td>
                    <td>
                      {(transaction.quantity * transaction.price_per_unit).toLocaleString('tr-TR')} ₺
                      {transaction.fees > 0 && <span className="fees"> +{transaction.fees.toLocaleString('tr-TR')} ₺</span>}
                    </td>
                    <td>{transaction.notes || '-'}</td>
                    <td className="actions-cell">
                      <button 
                        className="delete-transaction-btn" 
                        onClick={() => handleDeleteTransaction(transaction.id)}
                        title="Sil"
                      >
                        ×
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                disabled={page === 1}
              >
                Önceki
              </button>
              <span>Sayfa {page} / {totalPages}</span>
              <button 
                onClick={() => setPage(prev => Math.min(prev + 1, totalPages))}
                disabled={page === totalPages}
              >
                Sonraki
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}