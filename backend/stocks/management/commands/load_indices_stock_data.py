# /Users/barispome/Desktop/Project/BORTAL/backend/stocks/management/commands/load_indices_stock_data.py

"""

BORTAL Stock and Index Data Loader

This command provides a comprehensive solution for loading and updating stock and index data for
the BORTAL Turkish stock market application. It integrates functionality from three previously
separate commands into a unified interface.

Features:
- Load basic stock information from a CSV file
- Load index definitions and constituents from a JSON file
- Fetch detailed stock and index data from Yahoo Finance API
- Calculate technical indicators for stocks

Usage Examples:
    # Complete data load (run all phases)
    python manage.py load_indices_stock_data

    # Initial database setup (load only from local files)
    python manage.py load_indices_stock_data --load-basic --load-indices

    # Update only historical prices
    python manage.py load_indices_stock_data --skip-fundamentals --skip-technicals
    
    # Update a specific stock
    python manage.py load_indices_stock_data --symbol THYAO
    
    # Update a specific index
    python manage.py load_indices_stock_data --index BIST100
    
    # Update only recent data
    python manage.py load_indices_stock_data --days 30
    
    # Recalculate technical indicators
    python manage.py load_indices_stock_data --skip-historical --skip-fundamentals --skip-indices

The command includes comprehensive error handling and progress logging to make data loading
operations transparent and debuggable.

"""



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
    TechnicalIndicator, IndexPrice
)


class Command(BaseCommand):
    help = "Load comprehensive stock and index data from CSV/JSON files and Yahoo Finance API"

    def add_arguments(self, parser):
        # Basic data loading options
        parser.add_argument(
            '--load-basic',
            action='store_true',
            help='Load basic stock data from CSV file'
        )
        parser.add_argument(
            '--load-indices',
            action='store_true',
            help='Load index definitions from JSON file'
        )
        
        # Yahoo Finance data loading options
        parser.add_argument(
            '--days',
            type=int,
            default=365*5,
            help='Number of days of historical data to fetch (default: 365)'
        )
        parser.add_argument(
            '--symbol',
            type=str,
            help='Fetch data for a specific stock symbol only'
        )
        parser.add_argument(
            '--index',
            type=str,
            help='Fetch data for a specific index only'
        )
        
        # Data type filtering options
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
        parser.add_argument(
            '--skip-indices',
            action='store_true',
            help='Skip loading index price data'
        )

    def handle(self, *args, **options):
        # Extract options
        load_basic = options.get('load_basic', False)
        load_indices = options.get('load_indices', False)
        days = options.get('days', 365)
        specific_symbol = options.get('symbol')
        specific_index = options.get('index')
        skip_historical = options.get('skip_historical', False)
        skip_fundamentals = options.get('skip_fundamentals', False)
        skip_technicals = options.get('skip_technicals', False)
        skip_indices = options.get('skip_indices', False)
        
        # If no specific load option is provided, assume we're loading everything
        if not any([load_basic, load_indices, specific_symbol, specific_index]):
            load_basic = True
            load_indices = True
        
        # Step 1: Load basic stock data from CSV if requested
        if load_basic:
            self.load_basic_stock_data()
        
        # Step 2: Load index definitions from JSON if requested
        if load_indices:
            self.load_index_definitions()
        
        # Step 3: Load stock data from Yahoo Finance
        if not skip_indices and not specific_symbol:
            self.load_index_prices(days, specific_index)
        
        # Step 4: Load detailed stock data if not explicitly skipped
        if not specific_index:
            self.load_stock_data(
                days, 
                specific_symbol, 
                skip_historical, 
                skip_fundamentals, 
                skip_technicals
            )
        
        self.stdout.write(self.style.SUCCESS("\n✅ All data loading operations completed!"))

    def load_basic_stock_data(self):
        """Load basic stock data from CSV file"""
        self.stdout.write("\n🔄 Loading basic stock data from CSV...")
        
        data_path = os.path.join(settings.BASE_DIR, 'data')
        csv_path = os.path.join(data_path, 'Şirketler.csv')

        try:
            df = pd.read_csv(csv_path, header=None)
            df.columns = ['ticker', 'name']
        except FileNotFoundError:
            self.stderr.write("❌ Error: 'Şirketler.csv' not found in /data directory.")
            return
        except Exception as e:
            self.stderr.write(f"❌ Error reading CSV: {e}")
            return

        created_count = 0
        updated_count = 0
        for _, row in df.iterrows():
            symbol = str(row['ticker']).strip()
            name = str(row['name']).strip()

            stock, created = Stock.objects.get_or_create(
                symbol=symbol,
                defaults={'name': name, 'is_active': True}
            )

            if not created:
                stock.name = name
                stock.save()
                updated_count += 1
            else:
                created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'✅ Basic stock data: Added {created_count}, Updated {updated_count} stocks'))

    def load_index_definitions(self):
        """Load index definitions and their constituent stocks from JSON file"""
        self.stdout.write("\n🔄 Loading index definitions from JSON...")
        
        data_path = os.path.join(settings.BASE_DIR, 'data')
        json_path = os.path.join(data_path, 'Endeksler.json')

        try:
            with open(json_path, 'r') as file:
                indices_data = json.load(file)
        except FileNotFoundError:
            self.stderr.write("❌ Error: 'Endeksler.json' not found in /data directory.")
            return
        except json.JSONDecodeError as e:
            self.stderr.write(f"❌ Error decoding JSON: {e}")
            return
        except Exception as e:
            self.stderr.write(f"❌ Error reading JSON file: {e}")
            return

        # Process each index and its stocks
        for index_name, stock_symbols in indices_data.items():
            # Create or get the index
            index, created = Index.objects.get_or_create(
                name=index_name,
                defaults={
                    'display_name': index_name.replace('_', ' '),
                    'region': 'Turkey'
                }
            )
            
            status = "Created" if created else "Updated"
            self.stdout.write(f'📊 {status} index: {index_name}')
            
            # Add stocks to the index
            added_count = 0
            not_found_count = 0
            
            for symbol in stock_symbols:
                try:
                    stock = Stock.objects.get(symbol=symbol)
                    stock.indices.add(index)
                    added_count += 1
                except Stock.DoesNotExist:
                    self.stderr.write(f"⚠️ Stock with symbol '{symbol}' not found, skipping")
                    not_found_count += 1
            
            self.stdout.write(f'  ✅ Added {added_count} stocks to {index_name} index')
            if not_found_count > 0:
                self.stdout.write(f'  ⚠️ {not_found_count} stocks from {index_name} index were not found in the database')

    def load_index_prices(self, days, specific_index=None):
        """Load index price data from Yahoo Finance"""
        self.stdout.write("\n🔄 Loading index price data from Yahoo Finance...")
        
        # Map of BIST index names to Yahoo Finance symbols
        # These are the main indices for BIST (Istanbul Stock Exchange)
        INDEX_MAPPING = {
            # Main indices (from your current mapping)
            'BIST100': 'XU100.IS',         # BIST 100 Index
            'BIST30': 'XU030.IS',          # BIST 30 Index
            'BIST50': 'XU050.IS',          # BIST 50 Index
            'BIST_BANKA': 'XBANK.IS',      # BIST Bank Index (renamed from 'BIST BANKA')
            'BIST_SINAI': 'XUSIN.IS',      # BIST Industrials Index (renamed from 'BIST SINAI')
            'BIST_MALI': 'XUMAL.IS',       # BIST Financials Index (renamed from 'BIST MALI')
            'BIST_TEKNOLOJI': 'XUTEK.IS',  # BIST Technology Index (renamed from 'BIST TEKNOLOJI')
            'BIST_HOLDING_YATIRIM': 'XHOLD.IS',  # BIST Holding & Investment Index (renamed from 'BIST HOLDING')
            
            # Additional sector indices (from your JSON file)
            'BIST_KOBI_SANAYI': 'XKOBI.IS',        # BIST SME Industrial Index
            'BIST_TEMETTU_25': 'XTMTU.IS',         # BIST Dividend 25 Index
            'BIST_GIDA_ICECEK': 'XGIDA.IS',        # BIST Food & Beverage Index
            'BIST_KIMYA_PETROL_PLASTIK': 'XKMYA.IS', # BIST Chemical, Petroleum, Plastic Index
            'BIST_MADENCILIK': 'XMADN.IS',         # BIST Mining Index
            'BIST_METAL_ANA': 'XMANA.IS',          # BIST Basic Metal Index
            'BIST_METAL_ESYA_MAKINA': 'XMESY.IS',  # BIST Metal Products & Machinery Index
            'BIST_ORMAN_KAGIT_BASIM': 'XKAGT.IS',  # BIST Wood, Paper, Printing Index
            'BIST_TAS_TOPRAK': 'XTAST.IS',         # BIST Non-Metal Mineral Products Index
            'BIST_TEKSTIL_DERI': 'XTEKS.IS',       # BIST Textile, Leather Index
            'BIST_HIZMETLER': 'XUHIZ.IS',          # BIST Services Index
            'BIST_ELEKTRIK': 'XELKT.IS',           # BIST Electricity Index
            'BIST_İLETİŞİM': 'XILTM.IS',           # BIST Telecommunication Index
            'BIST_INSAAT': 'XINSA.IS',             # BIST Construction Index
            'BIST_TICARET': 'XTCRT.IS',            # BIST Wholesale & Retail Trade Index
            'BIST_TURIZM': 'XTRZM.IS',             # BIST Tourism Index
            'BIST_ULASTIRMA': 'XULAS.IS',          # BIST Transportation Index
            'BIST_SIGORTA': 'XSGRT.IS',            # BIST Insurance Index
            'BIST_FIN_KIR_FAKTORING': 'XFINK.IS',  # BIST Leasing & Factoring Index
            'BIST_BILISIM': 'XBLSM.IS'             # BIST Information Technology Index
        }
        
        # Get indices to process
        if specific_index:
            if specific_index in INDEX_MAPPING:
                indices = Index.objects.filter(name=specific_index)
                if not indices.exists():
                    # Create the index if it doesn't exist
                    indices = [Index.objects.create(
                        name=specific_index,
                        display_name=specific_index,
                        region='Turkey'
                    )]
            else:
                self.stderr.write(f"❌ Index '{specific_index}' not found in the mapping.")
                self.stdout.write(f"Available indices: {', '.join(INDEX_MAPPING.keys())}")
                return
        else:
            # Process all indices in the mapping
            indices = []
            for index_name in INDEX_MAPPING.keys():
                index, created = Index.objects.get_or_create(
                    name=index_name,
                    defaults={
                        'display_name': index_name,
                        'region': 'Turkey'
                    }
                )
                indices.append(index)
        
        self.stdout.write(f"🔍 Processing {len(indices)} indices...")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Process each index
        for index in indices:
            if index.name not in INDEX_MAPPING:
                self.stderr.write(f"⚠️ No Yahoo Finance symbol mapping for {index.name}, skipping")
                continue
                
            yahoo_symbol = INDEX_MAPPING[index.name]
            self.stdout.write(f"\n📊 Processing {index.name} ({yahoo_symbol})")
            
            try:
                # Fetch the index data from Yahoo Finance
                yf_index = yf.Ticker(yahoo_symbol)
                
                # Get historical data
                hist = yf_index.history(
                    start=start_date.strftime('%Y-%m-%d'), 
                    end=end_date.strftime('%Y-%m-%d')
                )
                
                if hist.empty:
                    self.stderr.write(f"  ⚠️ No historical data available for {index.name}")
                    continue
                
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
                    price, created = IndexPrice.objects.update_or_create(
                        index=index,
                        date=date,
                        defaults={
                            'open': row['Open'],
                            'high': row['High'],
                            'low': row['Low'],
                            'close': row['Close'],
                            'volume': int(row['Volume'])
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                self.stdout.write(f"  ✅ Prices: Added {created_count}, Updated {updated_count} records")
                
                # Update index info if available
                try:
                    info = yf_index.info
                    if 'longName' in info and info['longName']:
                        index.display_name = info['longName']
                        index.save()
                        self.stdout.write(f"  ✅ Updated index display name to: {info['longName']}")
                except Exception as e:
                    self.stderr.write(f"  ⚠️ Could not update index info: {str(e)}")
                
                # Pause to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.stderr.write(f"❌ Error processing {index.name}: {str(e)}")
                continue

    def load_stock_data(self, days, specific_symbol=None, skip_historical=False, 
                        skip_fundamentals=False, skip_technicals=False):
        """Load detailed stock data from Yahoo Finance"""
        self.stdout.write("\n🔄 Loading detailed stock data from Yahoo Finance...")
        
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