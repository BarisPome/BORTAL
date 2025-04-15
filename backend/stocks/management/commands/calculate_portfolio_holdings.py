from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Cast
from stocks.models import Portfolio, PortfolioTransaction, PortfolioHolding, Stock, StockPrice
from django.utils import timezone


class Command(BaseCommand):
    help = "Calculate and update portfolio holdings based on transactions"

    def add_arguments(self, parser):
        parser.add_argument(
            '--portfolio',
            type=str,
            help='Calculate holdings for a specific portfolio UUID only'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Calculate holdings for all portfolios of a specific user ID'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Recalculate all portfolio holdings in the system'
        )

    def handle(self, *args, **options):
        portfolio_uuid = options.get('portfolio')
        user_id = options.get('user')
        recalculate_all = options.get('all')
        
        # Determine which portfolios to process
        if portfolio_uuid:
            portfolios = Portfolio.objects.filter(id=portfolio_uuid)
            if not portfolios.exists():
                self.stderr.write(f"❌ Portfolio with UUID '{portfolio_uuid}' not found.")
                return
        elif user_id:
            portfolios = Portfolio.objects.filter(user__id=user_id)
            if not portfolios.exists():
                self.stderr.write(f"❌ No portfolios found for user ID '{user_id}'.")
                return
        elif recalculate_all:
            portfolios = Portfolio.objects.all()
        else:
            self.stderr.write("❌ Please specify --portfolio, --user, or --all")
            return
        
        self.stdout.write(f"🔍 Processing {portfolios.count()} portfolios...")
        
        # Process each portfolio
        for portfolio in portfolios:
            self.stdout.write(f"\n💼 Processing portfolio: {portfolio.name} (Owner: {portfolio.user.username})")
            
            # Get all transactions for this portfolio
            transactions = PortfolioTransaction.objects.filter(portfolio=portfolio).order_by('transaction_date')
            
            if not transactions.exists():
                self.stdout.write(f"  ℹ️ No transactions found for this portfolio.")
                continue
            
            # Get distinct stocks in this portfolio
            stock_ids = transactions.values_list('stock', flat=True).distinct()
            stocks = Stock.objects.filter(id__in=stock_ids)
            
            # Clear existing holdings
            PortfolioHolding.objects.filter(portfolio=portfolio).delete()
            self.stdout.write(f"  🔄 Cleared existing holdings")
            
            # Calculate holdings for each stock
            for stock in stocks:
                self.stdout.write(f"  📈 Calculating {stock.symbol}...")
                
                # Get all transactions for this stock
                stock_transactions = transactions.filter(stock=stock)
                
                # Initialize variables
                total_quantity = Decimal('0')
                total_cost = Decimal('0')
                
                # Process each transaction
                for tx in stock_transactions:
                    # Buy transaction
                    if tx.transaction_type == 'buy':
                        transaction_cost = tx.quantity * tx.price_per_unit + tx.fees
                        total_cost += transaction_cost
                        total_quantity += tx.quantity
                    
                    # Sell transaction
                    elif tx.transaction_type == 'sell':
                        if total_quantity > 0:
                            # Calculate proportion of cost to remove
                            proportion_sold = min(tx.quantity / total_quantity, Decimal('1'))
                            cost_removed = total_cost * proportion_sold
                            total_cost -= cost_removed
                            total_quantity -= tx.quantity
                    
                    # Dividend transaction
                    elif tx.transaction_type == 'dividend':
                        # Dividends don't affect quantity, just reduce cost basis
                        total_cost -= tx.quantity * tx.price_per_unit
                
                # Only create holding if quantity > 0
                if total_quantity > 0:
                    average_cost = total_cost / total_quantity if total_quantity > 0 else Decimal('0')
                    
                    # Create