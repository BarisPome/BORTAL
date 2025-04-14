import yfinance as yf

class YahooFinanceService:
    """
    Service class for interacting with Yahoo Finance API
    """
    def get_stock_detail(self, symbol):
        # Format the symbol correctly for Turkish stocks
        yahoo_symbol = f"{symbol}.IS"
        
        # Fetch the stock data
        stock = yf.Ticker(yahoo_symbol)
        
        # Get basic info
        info = stock.info
        
        # Get historical data (last 30 days)
        hist = stock.history(period="30d")
        
        # Convert historical data to a format suitable for JSON
        historical_data = []
        for date, row in hist.iterrows():
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(row['Open'], 2),
                'high': round(row['High'], 2),
                'low': round(row['Low'], 2),
                'close': round(row['Close'], 2),
                'volume': int(row['Volume'])
            })
        
        # Prepare response data
        response_data = {
            'symbol': symbol,
            'name': info.get('longName', ''),
            'current_price': info.get('currentPrice', 0),
            'previous_close': info.get('previousClose', 0),
            'open': info.get('open', 0),
            'day_high': info.get('dayHigh', 0),
            'day_low': info.get('dayLow', 0),
            'volume': info.get('volume', 0),
            'average_volume': info.get('averageVolume', 0),
            'market_cap': info.get('marketCap', 0),
            'PE_ratio': info.get('trailingPE', 0),
            'EPS': info.get('trailingEps', 0),
            'dividend_yield': info.get('dividendYield', 0) if info.get('dividendYield') else 0,
            'historical_data': historical_data
        }
        
        return response_data