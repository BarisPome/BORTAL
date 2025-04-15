#!/usr/bin/env python
"""
BIST Stock Market Portal (BORTAL) - Full Database Update Script
"""

import os
import sys
import argparse
import logging
import time
import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

from django.core.management import call_command

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update_data.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Update all BORTAL database data')
    parser.add_argument(
        '--days',
        type=int, 
        default=365,
        help='Number of days of historical data to fetch (default: 365)'
    )
    parser.add_argument(
        '--limit',
        action='store_true',
        help='Limit data fetching to reduce API calls (for testing)'
    )
    parser.add_argument(
        '--skip-news',
        action='store_true',
        help='Skip updating news data'
    )
    parser.add_argument(
        '--skip-analysis',
        action='store_true',
        help='Skip analytical calculations (correlations, etc.)'
    )
    return parser.parse_args()

def run_command(command_name, *args, **kwargs):
    """Run a Django management command and log the result"""
    start_time = time.time()
    logger.info(f"Starting {command_name}...")
    
    try:
        call_command(command_name, *args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"✅ {command_name} completed successfully in {elapsed:.2f} seconds")
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ {command_name} failed after {elapsed:.2f} seconds: {str(e)}")
        return False

def main():
    """Main execution function"""
    start_time = time.time()
    logger.info("=" * 80)
    logger.info(f"BORTAL Database Update - Started at {datetime.datetime.now()}")
    logger.info("=" * 80)
    
    args = parse_arguments()
    
    # Step 1: Load basic stock and index data
    run_command('load_data')
    run_command('load_indices')
    
    # Step 2: Update index price data
    if args.limit:
        run_command('load_index_prices', days=30)
    else:
        run_command('load_index_prices', days=args.days)
    
    # Step 3: Update comprehensive stock data
    if args.limit:
        # For testing, just update BIST30 stocks
        try:
            from stocks.models import Stock, Index
            bist30_stocks = Stock.objects.filter(indices__name='BIST30')
            for stock in bist30_stocks[:5]:  # First 5 stocks only
                run_command('load_stock_data', symbol=stock.symbol, days=30)
        except Exception as e:
            logger.error(f"Error limiting stock updates: {str(e)}")
            # Fallback to a very limited update
            run_command('load_stock_data', days=7)
    else:
        # Full update of all stocks
        run_command('load_stock_data', days=args.days)
    
    # Step 4: Update news data (if not skipped)
    if not args.skip_news:
        news_days = 7 if args.limit else 30
        run_command('fetch_news', days=news_days)
    
    # Step 5: Run analysis commands (if not skipped)
    if not args.skip_analysis:
        # Update portfolio holdings
        run_command('calculate_portfolio_holdings', all=True)
        
        # Calculate portfolio performance
        performance_days = 30 if args.limit else 90
        run_command('portfolio_performance', days=performance_days)
        
        # Calculate stock correlations
        correlation_days = 30 if args.limit else 90
        run_command('stock_correlations', days=correlation_days)
    
    # Step 6: Ensure all users have default watchlists and portfolios
    run_command('setup_user_defaults', all=True)
    
    # Complete
    total_time = time.time() - start_time
    logger.info("=" * 80)
    logger.info(f"BORTAL Database Update - Completed in {total_time:.2f} seconds")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()