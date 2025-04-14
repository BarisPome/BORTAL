// src/utils/formatters.js
export const formatCurrency = (value) => {
    return new Intl.NumberFormat('tr-TR', { 
      style: 'currency', 
      currency: 'TRY' 
    }).format(value);
  };
  
  export const formatNumber = (value) => {
    return new Intl.NumberFormat('tr-TR').format(value);
  };
  
  export const formatPercentage = (value) => {
    return new Intl.NumberFormat('tr-TR', { 
      style: 'percent', 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    }).format(value / 100);
  };