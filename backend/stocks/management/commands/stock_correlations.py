import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db.models import Min, Max
from stocks.models import Stock, StockPrice, Index, SystemSetting


class Command(BaseCommand):
    help = "Calculate correlations between stocks for analysis"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days of historical data to use (default: 90)'
        )
        parser.add_argument(
            '--index',
            type=str,
            default='BIST100',
            help='Calculate correlations for stocks in a specific index (default: BIST100)'
        )
        parser.add_argument(
            '--min-pairs',
            type=int,
            default=10,
            help='Minimum number of price pairs needed to calculate correlation (default: 10)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Optional path to save correlation matrix as CSV'
        )

    def handle(self, *args, **options):
        days = options['days']
        index_name = options['index']
        min_pairs = options['min_pairs']
        output_path = options.get('output')
        
        # Get the specified index
        try:
            index = Index.objects.get(name=index_name)
            self.stdout.write(f"📊 Processing stocks in {index.name} index")
        except Index.DoesNotExist:
            self.stderr.write(f"❌ Index '{index_name}' not found.")
            return
        
        # Get all stocks in the index
        stocks = Stock.objects.filter(indices=index, is_active=True)
        
        if not stocks.exists():
            self.stderr.write(f"❌ No stocks found in the {index_name} index.")
            return
        
        self.stdout.write(f"🔍 Found {stocks.count()} stocks in {index_name}")
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        self.stdout.write(f"📅 Analyzing price correlations from {start_date} to {end_date}")
        
        # Collect closing prices for each stock
        stock_prices = {}
        
        for stock in stocks:
            # Get all prices for this stock in the date range
            prices = StockPrice.objects.filter(
                stock=stock,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            if prices.count() < min_pairs:
                self.stdout.write(f"⚠️ Skipping {stock.symbol}: insufficient price data (found {prices.count()}, need {min_pairs})")
                continue
            
            # Add to our dictionary
            stock_prices[stock.symbol] = {
                price.date.isoformat(): float(price.close)
                for price in prices
            }
        
        if len(stock_prices) < 2:
            self.stderr.write(f"❌ Not enough stocks with sufficient price data to calculate correlations.")
            return
        
        self.stdout.write(f"📈 Calculating correlations for {len(stock_prices)} stocks")
        
        # Convert to DataFrame for easier correlation calculation
        # First get all unique dates
        all_dates = set()
        for prices in stock_prices.values():
            all_dates.update(prices.keys())
        all_dates = sorted(all_dates)
        
        # Create DataFrame with dates as index
        df = pd.DataFrame(index=all_dates)
        
        # Add each stock's prices as a column
        for symbol, prices in stock_prices.items():
            df[symbol] = pd.Series(prices)
        
        # Calculate correlation matrix
        correlation_matrix = df.corr(min_periods=min_pairs)
        
        # Store results
        results = {}
        
        # Get correlations for each stock
        for stock_symbol in correlation_matrix.columns:
            # Get top 5 most positively correlated stocks
            top_positive = correlation_matrix[stock_symbol].drop(stock_symbol).nlargest(5)
            # Get top 5 most negatively correlated stocks
            top_negative = correlation_matrix[stock_symbol].drop(stock_symbol).nsmallest(5)
            # Get average correlation
            avg_correlation = correlation_matrix[stock_symbol].drop(stock_symbol).mean()
            
            results[stock_symbol] = {
                'top_positive': {
                    symbol: round(float(corr), 4)
                    for symbol, corr in top_positive.items()
                },
                'top_negative': {
                    symbol: round(float(corr), 4)
                    for symbol, corr in top_negative.items()
                },
                'average_correlation': round(float(avg_correlation), 4)
            }
        
        # Find overall most and least correlated pairs
        correlations = []
        for i, stock1 in enumerate(correlation_matrix.columns):
            for stock2 in correlation_matrix.columns[i+1:]:
                correlations.append((
                    stock1, 
                    stock2, 
                    float(correlation_matrix.loc[stock1, stock2])
                ))
        
        # Sort by correlation value
        correlations.sort(key=lambda x: x[2])
        
        # Get top and bottom 10 pairs
        most_negative_pairs = correlations[:10]
        most_positive_pairs = correlations[-10:][::-1]  # Reverse to get highest first
        
        # Calculate average correlation across all stocks
        total_correlation = sum(corr for _, _, corr in correlations)
        avg_market_correlation = total_correlation / len(correlations) if correlations else 0
        
        # Create summary
        summary = {
            'index': index_name,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'stocks_analyzed': len(stock_prices),
            'average_market_correlation': round(avg_market_correlation, 4),
            'most_positively_correlated_pairs': [
                {'pair': [s1, s2], 'correlation': round(corr, 4)}
                for s1, s2, corr in most_positive_pairs
            ],
            'most_negatively_correlated_pairs': [
                {'pair': [s1, s2], 'correlation': round(corr, 4)}
                for s1, s2, corr in most_negative_pairs
            ],
            'stock_details': results
        }
        
        # Save results to system settings
        SystemSetting.objects.update_or_create(
            key=f'correlation_matrix_{index_name}',
            defaults={
                'value': json.dumps(summary),
                'description': f'Stock correlation data for {index_name} index'
            }
        )
        
        # Output to console
        self.stdout.write(f"\n📊 Correlation Analysis for {index_name}")
        self.stdout.write(f"📅 Period: {start_date} to {end_date} ({days} days)")
        self.stdout.write(f"📈 Stocks analyzed: {len(stock_prices)}")
        self.stdout.write(f"🔄 Average market correlation: {round(avg_market_correlation, 4)}")
        
        self.stdout.write("\n🔝 Most positively correlated pairs:")
        for s1, s2, corr in most_positive_pairs:
            self.stdout.write(f"  {s1} & {s2}: {round(corr, 4)}")
        
        self.stdout.write("\n🔻 Most negatively correlated pairs:")
        for s1, s2, corr in most_negative_pairs:
            self.stdout.write(f"  {s1} & {s2}: {round(corr, 4)}")
        
        # Save to CSV if output path provided
        if output_path:
            try:
                correlation_matrix.to_csv(output_path)
                self.stdout.write(f"\n✅ Correlation matrix saved to {output_path}")
            except Exception as e:
                self.stderr.write(f"❌ Error saving correlation matrix: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Correlation analysis completed!"))