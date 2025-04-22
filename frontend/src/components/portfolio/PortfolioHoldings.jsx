import React, { useState } from 'react';
import '../../styles/components/portfolio/PortfolioHoldings.css';


export default function PortfolioHoldings({ holdings = [], onAddTransaction, onDeleteHolding }) {
  const [sortField, setSortField] = useState('symbol');
  const [sortDirection, setSortDirection] = useState('asc');

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const sortedHoldings = [...holdings].sort((a, b) => {
    const aValue = sortField === 'profit_loss_percent' ? a.profit_loss_percent : 
                  sortField === 'current_value' ? a.current_value : 
                  sortField === 'quantity' ? a.quantity : a.stock.symbol;
    
    const bValue = sortField === 'profit_loss_percent' ? b.profit_loss_percent : 
                  sortField === 'current_value' ? b.current_value : 
                  sortField === 'quantity' ? b.quantity : b.stock.symbol;
    
    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  if (holdings.length === 0) {
    return (
      <div className="holdings-empty">
        <p>Portföyünüzde henüz hisse bulunmuyor.</p>
        <button className="add-transaction-btn" onClick={() => onAddTransaction()}>
          Hisse Ekle
        </button>
      </div>
    );
  }

  return (
    <div className="portfolio-holdings">
      <div className="holdings-header">
        <h3>Hisse Senetleri</h3>
        <button className="add-transaction-btn" onClick={() => onAddTransaction()}>
          İşlem Ekle
        </button>
      </div>

      <div className="holdings-table-container">
        <table className="holdings-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('symbol')} className={sortField === 'symbol' ? sortDirection : ''}>
                Sembol
                {sortField === 'symbol' && <span className="sort-arrow">{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th>İsim</th>
              <th onClick={() => handleSort('quantity')} className={sortField === 'quantity' ? sortDirection : ''}>
                Adet
                {sortField === 'quantity' && <span className="sort-arrow">{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th>Ortalama Maliyet</th>
              <th>Son Fiyat</th>
              <th onClick={() => handleSort('current_value')} className={sortField === 'current_value' ? sortDirection : ''}>
                Güncel Değer
                {sortField === 'current_value' && <span className="sort-arrow">{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th onClick={() => handleSort('profit_loss_percent')} className={sortField === 'profit_loss_percent' ? sortDirection : ''}>
                Kar/Zarar
                {sortField === 'profit_loss_percent' && <span className="sort-arrow">{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {sortedHoldings.map((holding) => (
              <tr key={holding.stock.symbol}>
                <td className="symbol-cell">{holding.stock.symbol}</td>
                <td>{holding.stock.name}</td>
                <td>{holding.quantity}</td>
                <td>{holding.average_cost.toLocaleString('tr-TR')} ₺</td>
                <td>{holding.last_price.toLocaleString('tr-TR')} ₺</td>
                <td>{holding.current_value.toLocaleString('tr-TR')} ₺</td>
                <td className={`profit-loss ${holding.profit_loss_percent >= 0 ? 'positive' : 'negative'}`}>
                  {holding.profit_loss_percent.toFixed(2)}%
                </td>
                <td className="actions-cell">
                  <button 
                    className="transaction-btn" 
                    onClick={() => onAddTransaction(holding.stock)}
                    title="İşlem Ekle"
                  >
                    +
                  </button>
                  <button 
                    className="delete-holding-btn" 
                    onClick={() => onDeleteHolding(holding)}
                    title="Hisseyi Sil"
                  >
                    ×
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}