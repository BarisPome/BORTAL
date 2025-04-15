import os
import time
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from stocks.models import Index, IndexPrice


class Command(BaseCommand):
    help = "Load index price data from Yahoo Finance API"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days of historical data to fetch (default: 365)'
        )
        parser.add_argument(
            '--index',
            type=str,
            help='Fetch data for a specific index only'
        )

    def handle(self, *args, **options):
        days = options['days']
        specific_index = options.get('index')
        
        # Map of BIST index names to Yahoo Finance symbols
        # These are the main indices for BIST (Istanbul Stock Exchange)
        INDEX_MAPPING = {
            'BIST100': 'XU100.IS',    # BIST 100 Index
            'BIST30': 'XU030.IS',     # BIST 30 Index
            'BIST50': 'XU050.IS',     # BIST 50 Index
            'BIST BANKA': 'XBANK.IS', # BIST Bank Index
            'BIST SINAI': 'XUSIN.IS', # BIST Industrials Index
            'BIST MALI': 'XUMAL.IS',  # BIST Financials Index
            'BIST TEKNOLOJI': 'XUTEK.IS', # BIST Technology Index
            'BIST HOLDING': 'XHOLD.IS', # BIST Holding & Investment Index
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
        
        self.stdout.write(self.style.SUCCESS("\n✅ Index data loading completed!"))