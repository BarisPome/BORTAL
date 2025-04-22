import React, { useState, useEffect } from 'react';
import '../../styles/components/portfolio/TransactionModal.css';


export default function TransactionModal({ 
  isOpen, 
  onClose, 
  onSubmit, 
  initialStock = null,
  availableStocks = [] 
}) {
  const [formData, setFormData] = useState({
    stock_symbol: initialStock ? initialStock.symbol : '',
    transaction_type: 'buy',
    quantity: '',
    price_per_unit: '',
    fees: '0',
    transaction_date: new Date().toISOString().split('T')[0],
    notes: ''
  });
  
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [showStockDropdown, setShowStockDropdown] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (initialStock) {
      setFormData(prev => ({
        ...prev,
        stock_symbol: initialStock.symbol
      }));
      setSearchTerm(initialStock.symbol);
    }
  }, [initialStock]);

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredStocks([]);
      return;
    }
    
    const filtered = availableStocks.filter(stock => 
      stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) || 
      stock.name.toLowerCase().includes(searchTerm.toLowerCase())
    ).slice(0, 10);
    
    setFilteredStocks(filtered);
  }, [searchTerm, availableStocks]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear error when field is changed
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setShowStockDropdown(true);
    
    // Update form data only if a stock is selected
    if (e.target.value === '') {
      setFormData({
        ...formData,
        stock_symbol: ''
      });
    }
  };

  const handleStockSelect = (stock) => {
    setFormData({
      ...formData,
      stock_symbol: stock.symbol
    });
    setSearchTerm(stock.symbol);
    setShowStockDropdown(false);
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.stock_symbol) {
      newErrors.stock_symbol = 'Hisse senedi seçiniz';
    }
    
    if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
      newErrors.quantity = 'Geçerli bir adet giriniz';
    }
    
    if (!formData.price_per_unit || parseFloat(formData.price_per_unit) <= 0) {
      newErrors.price_per_unit = 'Geçerli bir fiyat giriniz';
    }
    
    if (!formData.transaction_date) {
      newErrors.transaction_date = 'Tarih seçiniz';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    // Convert numeric strings to numbers
    const processedData = {
      ...formData,
      quantity: parseFloat(formData.quantity),
      price_per_unit: parseFloat(formData.price_per_unit),
      fees: parseFloat(formData.fees || 0)
    };
    
    onSubmit(processedData);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="transaction-modal">
        <div className="modal-header">
          <h2>Yeni İşlem Ekle</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Hisse Senedi</label>
            <div className="stock-search">
              <input
                type="text"
                placeholder="Hisse senedi ara (THYAO, Türk Hava...)"
                value={searchTerm}
                onChange={handleSearchChange}
                onFocus={() => setShowStockDropdown(true)}
                className={errors.stock_symbol ? 'error' : ''}
              />
              {showStockDropdown && filteredStocks.length > 0 && (
                <div className="stock-dropdown">
                  {filteredStocks.map((stock) => (
                    <div 
                      key={stock.symbol} 
                      className="stock-option"
                      onClick={() => handleStockSelect(stock)}
                    >
                      <span className="stock-symbol">{stock.symbol}</span>
                      <span className="stock-name">{stock.name}</span>
                    </div>
                  ))}
                </div>
              )}
              {errors.stock_symbol && <div className="error-message">{errors.stock_symbol}</div>}
            </div>
          </div>
          
          <div className="form-group">
            <label>İşlem Tipi</label>
            <div className="transaction-type-selector">
              <label className={`type-option ${formData.transaction_type === 'buy' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="transaction_type"
                  value="buy"
                  checked={formData.transaction_type === 'buy'}
                  onChange={handleChange}
                />
                Alış
              </label>
              <label className={`type-option ${formData.transaction_type === 'sell' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="transaction_type"
                  value="sell"
                  checked={formData.transaction_type === 'sell'}
                  onChange={handleChange}
                />
                Satış
              </label>
              <label className={`type-option ${formData.transaction_type === 'dividend' ? 'selected' : ''}`}>
                <input
                  type="radio"
                  name="transaction_type"
                  value="dividend"
                  checked={formData.transaction_type === 'dividend'}
                  onChange={handleChange}
                />
                Temettü
              </label>
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label>Adet</label>
              <input
                type="number"
                name="quantity"
                value={formData.quantity}
                onChange={handleChange}
                step="0.000001"
                min="0.000001"
                placeholder="0.00"
                className={errors.quantity ? 'error' : ''}
              />
              {errors.quantity && <div className="error-message">{errors.quantity}</div>}
            </div>
            
            <div className="form-group">
              <label>
                {formData.transaction_type === 'dividend' ? 'Temettü Tutarı (adet başına)' : 'Birim Fiyat'}
              </label>
              <input
                type="number"
                name="price_per_unit"
                value={formData.price_per_unit}
                onChange={handleChange}
                step="0.01"
                min="0.01"
                placeholder="0.00"
                className={errors.price_per_unit ? 'error' : ''}
              />
              {errors.price_per_unit && <div className="error-message">{errors.price_per_unit}</div>}
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label>İşlem Tarihi</label>
              <input
                type="date"
                name="transaction_date"
                value={formData.transaction_date}
                onChange={handleChange}
                className={errors.transaction_date ? 'error' : ''}
              />
              {errors.transaction_date && <div className="error-message">{errors.transaction_date}</div>}
            </div>
            
            <div className="form-group">
              <label>Komisyon ve Diğer Ücretler</label>
              <input
                type="number"
                name="fees"
                value={formData.fees}
                onChange={handleChange}
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </div>
          </div>
          
          <div className="form-group">
            <label>Notlar (İsteğe Bağlı)</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="İşlemle ilgili notlar..."
            />
          </div>
          
          <div className="transaction-summary">
            <h4>İşlem Özeti</h4>
            <div className="summary-details">
              <div className="summary-row">
                <span>Toplam Tutar:</span>
                <span className="summary-amount">
                  {!isNaN(parseFloat(formData.price_per_unit) * parseFloat(formData.quantity || 0)) 
                    ? (parseFloat(formData.price_per_unit) * parseFloat(formData.quantity || 0)).toLocaleString('tr-TR')
                    : '0'} ₺
                </span>
              </div>
              {parseFloat(formData.fees || 0) > 0 && (
                <div className="summary-row">
                  <span>Komisyon ve Ücretler:</span>
                  <span className="summary-fees">+{parseFloat(formData.fees).toLocaleString('tr-TR')} ₺</span>
                </div>
              )}
              <div className="summary-row total">
                <span>Genel Toplam:</span>
                <span className="summary-total">
                  {!isNaN(parseFloat(formData.price_per_unit) * parseFloat(formData.quantity || 0) + parseFloat(formData.fees || 0))
                    ? (parseFloat(formData.price_per_unit) * parseFloat(formData.quantity || 0) + parseFloat(formData.fees || 0)).toLocaleString('tr-TR')
                    : '0'} ₺
                </span>
              </div>
            </div>
          </div>
          
          <div className="form-actions">
            <button type="button" className="cancel-btn" onClick={onClose}>İptal</button>
            <button type="submit" className="submit-btn">İşlemi Kaydet</button>
          </div>
        </form>
      </div>
    </div>
  );
}