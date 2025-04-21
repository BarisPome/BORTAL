#!/usr/bin/env python
"""
BORTAL - Development Environment Setup Script
"""

import os
import sys
import json
import random
import csv
from pathlib import Path

from django.core.management import call_command

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()

# Import Django models
from django.contrib.auth.models import User
from stocks.models import Stock, Index





# Constants
DATA_DIR = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))
SAMPLE_COMPANIES_COUNT = 200
MAIN_INDICES = {
    'BIST100': 'Borsa Istanbul 100 Index',
    'BIST30': 'Borsa Istanbul 30 Index',
    'BIST50': 'Borsa Istanbul 50 Index',
    'BIST BANKA': 'Borsa Istanbul Bank Index',
    'BIST SINAI': 'Borsa Istanbul Industrials Index',
    'BIST MALI': 'Borsa Istanbul Financials Index',
    'BIST TEKNOLOJI': 'Borsa Istanbul Technology Index',
    'BIST HOLDING': 'Borsa Istanbul Holding & Investment Index'
}


def create_directory_structure():
    """Create necessary directories"""
    print("Creating directory structure...")
    
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    print("✅ Directory structure created")


def create_sample_data():
    """Create sample data files if they don't exist"""
    print("Checking for sample data files...")
    
    # Create sample companies CSV if it doesn't exist
    companies_file = DATA_DIR / 'Şirketler.csv'
    if not companies_file.exists():
        print(f"Generating sample companies file: {companies_file}")
        
        # Generate sample companies
        sample_companies = []
        sectors = ['Bank', 'Technology', 'Energy', 'Retail', 'Manufacturing', 
                   'Food', 'Construction', 'Telecom', 'Healthcare', 'Transport']
        
        for i in range(1, SAMPLE_COMPANIES_COUNT + 1):
            ticker = f"{random.choice('ABCDEFGHIJKLMNOPRSTUVYZ')}{random.choice('ABCDEFGHIJKLMNOPRSTUVYZ')}{random.choice('ABCDEFGHIJKLMNOPRSTUVYZ')}A"
            sector = random.choice(sectors)
            name = f"{sector} Company {i}"
            sample_companies.append([ticker, name])
        
        # Write to CSV
        with open(companies_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(sample_companies)
        
        print(f"✅ Created sample companies file with {len(sample_companies)} companies")
    else:
        print(f"✓ Companies file already exists: {companies_file}")
    
    # Create sample indices JSON if it doesn't exist
    indices_file = DATA_DIR / 'Endeksler.json'
    if not indices_file.exists():
        print(f"Generating sample indices file: {indices_file}")
        
        indices_data = {}
        
        # Populate the main indices with random stocks
        for index_name in MAIN_INDICES.keys():
            # Determine how many stocks to include in each index
            if index_name == 'BIST100':
                count = 100
            elif index_name == 'BIST50':
                count = 50
            elif index_name == 'BIST30':
                count = 30
            else:
                # Sector indices with random number of stocks
                count = random.randint(20, 40)
            
            # Generate random stock tickers for this index
            # (this assumes the stocks have already been created with load_data)
            try:
                all_stocks = list(Stock.objects.values_list('symbol', flat=True))
                if len(all_stocks) >= count:
                    indices_data[index_name] = random.sample(all_stocks, count)
                else:
                    # If not enough stocks in the database, generate dummy tickers
                    indices_data[index_name] = [f"{random.choice('ABCDEFGHIJKLMNOPRSTUVYZ')}{random.choice('ABCDEFGHIJKLMNOPRSTUVYZ')}{random.choice('ABCDEFGHIJKLMNOPRSTUVYZ')}A" for _ in range(count)]
            except:
                # If database access fails, generate dummy tickers
                indices_data[index_name] = [f"{random.choice('ABCDEFGHIJKLMNOPRSTUVYZ')}{random.choice('ABCDEFGHIJKLMNOPRSTUVYZ')}{random.choice('ABCDEFGHIJKLMNOPRSTUVYZ')}A" for _ in range(count)]
        
        # Write to JSON
        with open(indices_file, 'w') as f:
            json.dump(indices_data, f, indent=2)
        
        print(f"✅ Created sample indices file with {len(indices_data)} indices")
    else:
        print(f"✓ Indices file already exists: {indices_file}")


def run_migrations():
    """Run database migrations"""
    print("\nRunning database migrations...")
    call_command('migrate')
    print("✅ Migrations complete")


def load_initial_data():
    """Load initial data into the database"""
    print("\nLoading initial data...")
    
    # Load basic stock data
    call_command('load_indices_stock_data')
    
    
    print("✅ Initial data loaded")


def create_superuser():
    """Create a superuser if none exists"""
    print("\nChecking for superuser...")
    
    if not User.objects.filter(is_superuser=True).exists():
        print("No superuser found. Creating superuser 'admin'...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        print("✅ Superuser created with username 'admin' and password 'adminpass'")
    else:
        print("✓ Superuser already exists")


def setup_dev_environment():
    """Main function to set up the development environment"""
    print("\n" + "="*60)
    print("BORTAL - Development Environment Setup")
    print("="*60 + "\n")
    
    # Create directory structure
    create_directory_structure()
    
    # Create sample data files
    create_sample_data()
    
    # Run migrations
    run_migrations()
    
    # Load initial data
    load_initial_data()
    
    # Create superuser
    create_superuser()
    
    print("\n" + "="*60)
    print("✅ BORTAL development environment setup complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    setup_dev_environment()