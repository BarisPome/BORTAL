# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/management/commands/load_stock_data.py

import os
import json
import time
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from stocks.models import (
    Stock, Sector, Index, StockPrice, StockFundamental,
    TechnicalIndicator, StockIndex
)


class Command(BaseCommand):
    help = "Load comprehensive stock data from Yahoo Finance API"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days of historical data to fetch (default: 365)'
        )
        parser.add_argument(
            '--symbol',
            type=str,
            help='Fetch data for a specific stock symbol only'
        )
        parser.add_argument(
            '--skip-historical',
            action='store_true',
            help='Skip loading historical price data'
        )
        parser.add_argument(
            '--skip-fundamentals',
            action='store_true',
            help='Skip loading fundamental data'
        )
        parser.add_argument(
            '--skip-technicals',
            action='store_true',
            help='Skip calculating technical indicators'
        )

    def handle(self, *args, **options):
        days = options['days']
        specific_symbol = options.get('symbol')
        skip_historical = options.get('skip_historical', False)
        skip_fundamentals = options.get('skip_fundamentals', False)
        skip_technicals = options.get('skip_technicals', False)
        
        # Get stocks to process
        if specific_symbol:
            stocks = Stock.objects.filter(symbol=specific_symbol)
            if not stocks.exists():
                self.stderr.write(f"❌ Stock with symbol '{specific_symbol}' not found.")
                return
        else:
            stocks = Stock.objects.filter(is_active=True)
        
        self.stdout.write(f"🔍 Processing {stocks.count()} stocks...")
        
        # Process each stock
        for stock in stocks:
            self.stdout.write(f"\n📈 Processing {stock.symbol} - {stock.name}")
            
            # Fetch the stock data from Yahoo Finance
            # Note: For Turkish stocks, append '.IS' to the symbol for Yahoo Finance
            yahoo_symbol = f"{stock.symbol}.IS" 
            
            try:
                yf_stock = yf.Ticker(yahoo_symbol)
                
                # Update basic stock info
                self._update_stock_info(stock, yf_stock)
                
                # Load historical prices if not skipped
                if not skip_historical:
                    self._load_historical_prices(stock, yf_stock, days)
                
                # Load fundamental data if not skipped
                if not skip_fundamentals:
                    self._load_fundamentals(stock, yf_stock)
                
                # Calculate technical indicators if not skipped and we have price data
                if not skip_technicals and StockPrice.objects.filter(stock=stock).exists():
                    self._calculate_technical_indicators(stock)
                
                # Pause to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.stderr.write(f"❌ Error processing {stock.symbol}: {str(e)}")
                continue
        
        self.stdout.write(self.style.SUCCESS("\n✅ Data loading completed!"))

    def _update_stock_info(self, stock, yf_stock):
        """Update basic stock information"""
        try:
            info = yf_stock.info
            
            # Update sector if available
            if 'sector' in info and info['sector']:
                sector_name = info['sector']
                sector, created = Sector.objects.get_or_create(
                    name=sector_name,
                    defaults={'display_name': sector_name}
                )
                stock.sector = sector
            
            # Update other basic fields
            if 'longName' in info and info['longName']:
                stock.name = info['longName']
            
            if 'country' in info and info['country']:
                stock.country = info['country']
            
            if 'exchange' in info and info['exchange']:
                stock.exchange = info['exchange']
            
            if 'currency' in info and info['currency']:
                stock.currency = info['currency']
            
            if 'longBusinessSummary' in info and info['longBusinessSummary']:
                stock.description = info['longBusinessSummary']
            
            stock.save()
            self.stdout.write(f"  ✅ Updated basic info for {stock.symbol}")
            
        except Exception as e:
            self.stderr.write(f"  ⚠️ Could not update basic info: {str(e)}")

    def _load_historical_prices(self, stock, yf_stock, days):
        """Load historical price data"""
        try:
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get historical data
            hist = yf_stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            
            if hist.empty:
                self.stderr.write(f"  ⚠️ No historical data available for {stock.symbol}")
                return
            
            # Reset index to make date a column
            hist.reset_index(inplace=True)
            
            # Store each day's data
            created_count = 0
            updated_count = 0
            
            for _, row in hist.iterrows():
                date = row['Date'].date()  # Convert timestamp to date
                
                # Skip if any essential data is missing
                if pd.isna(row['Open']) or pd.isna(row['Close']) or pd.isna(row['Volume']):
                    continue
                
                # Create or update price record
                price, created = StockPrice.objects.update_or_create(
                    stock=stock,
                    date=date,
                    defaults={
                        'open': row['Open'],
                        'high': row['High'],
                        'low': row['Low'],
                        'close': row['Close'],
                        'volume': int(row['Volume']),
                        'adjusted_close': row['Close'] if 'Adj Close' not in row else row['Adj Close']
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            self.stdout.write(f"  ✅ Prices: Added {created_count}, Updated {updated_count} records")
            
        except Exception as e:
            self.stderr.write(f"  ⚠️ Could not load historical prices: {str(e)}")

    def _load_fundamentals(self, stock, yf_stock):
        """Load fundamental financial data"""
        try:
            info = yf_stock.info
            today = datetime.now().date()
            
            # Extract fundamental metrics
            fundamentals = {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
                'eps': info.get('trailingEps') or info.get('forwardEps'),
                'dividend_yield': info.get('dividendYield'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'debt_to_equity': info.get('debtToEquity'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'revenue': info.get('totalRevenue'),
                'net_income': info.get('netIncomeToCommon'),
                'gross_margin': info.get('grossMargins'),
                'operating_margin': info.get('operatingMargins'),
                'profit_margin': info.get('profitMargins'),
                'free_cash_flow': info.get('freeCashflow'),
            }
            
            # Filter out None values
            fundamentals = {k: v for k, v in fundamentals.items() if v is not None}
            
            # Skip if we don't have any meaningful fundamental data
            if not fundamentals:
                self.stderr.write(f"  ⚠️ No fundamental data available for {stock.symbol}")
                return
            
            # Create or update fundamental record
            fundamental, created = StockFundamental.objects.update_or_create(
                stock=stock,
                date=today,
                defaults=fundamentals
            )
            
            status = "Created" if created else "Updated"
            self.stdout.write(f"  ✅ {status} fundamental data")
            
        except Exception as e:
            self.stderr.write(f"  ⚠️ Could not load fundamentals: {str(e)}")

    def _calculate_technical_indicators(self, stock):
        """Calculate and store technical indicators"""
        try:
            # Get price data ordered by date
            prices = StockPrice.objects.filter(stock=stock).order_by('date')
            
            if prices.count() < 200:
                self.stderr.write(f"  ⚠️ Not enough price data for technical indicators (need at least 200 days)")
                return
            
            # Create a pandas DataFrame from price data
            df = pd.DataFrame(list(prices.values('date', 'open', 'high', 'low', 'close', 'volume')))
            
            # Calculate indicators
            # RSI - 14 day
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            df['rsi_14'] = 100 - (100 / (1 + rs))
            
            # Moving Averages
            df['ma_5'] = df['close'].rolling(window=5).mean()
            df['ma_10'] = df['close'].rolling(window=10).mean()
            df['ma_20'] = df['close'].rolling(window=20).mean()
            df['ma_50'] = df['close'].rolling(window=50).mean()
            df['ma_100'] = df['close'].rolling(window=100).mean()
            df['ma_200'] = df['close'].rolling(window=200).mean()
            
            # MACD
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # Bollinger Bands (20-day, 2 standard deviations)
            df['bollinger_middle'] = df['ma_20']
            std_dev = df['close'].rolling(window=20).std()
            df['bollinger_upper'] = df['bollinger_middle'] + (std_dev * 2)
            df['bollinger_lower'] = df['bollinger_middle'] - (std_dev * 2)
            
            # Store the calculated indicators
            created_count = 0
            updated_count = 0
            
            for _, row in df.iterrows():
                # Skip rows with NaN values (common at the beginning of the series)
                if pd.isna(row['rsi_14']) or pd.isna(row['ma_200']):
                    continue
                
                # Create technical indicator records
                indicator, created = TechnicalIndicator.objects.update_or_create(
                    stock=stock,
                    date=row['date'],
                    defaults={
                        'rsi_14': row['rsi_14'],
                        'macd': row['macd'],
                        'macd_signal': row['macd_signal'],
                        'macd_histogram': row['macd_histogram'],
                        'bollinger_upper': row['bollinger_upper'],
                        'bollinger_middle': row['bollinger_middle'],
                        'bollinger_lower': row['bollinger_lower'],
                        'ma_5': row['ma_5'],
                        'ma_10': row['ma_10'],
                        'ma_20': row['ma_20'],
                        'ma_50': row['ma_50'],
                        'ma_100': row['ma_100'],
                        'ma_200': row['ma_200'],
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            self.stdout.write(f"  ✅ Technical indicators: Added {created_count}, Updated {updated_count} records")
            
        except Exception as e:
            self.stderr.write(f"  ⚠️ Could not calculate technical indicators: {str(e)}")