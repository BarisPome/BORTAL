from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from stocks.models import (
    UserProfile, Watchlist, Portfolio, Stock, Index
)


class Command(BaseCommand):
    help = "Set up default watchlists and portfolios for users"

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Set up defaults for a specific user (username or ID)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Set up defaults for all users who do not have them yet'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset and recreate default watchlists and portfolios'
        )

    def handle(self, *args, **options):
        specific_user = options.get('user')
        all_users = options.get('all')
        reset = options.get('reset')
        
        if not (specific_user or all_users):
            self.stderr.write("❌ Please specify either --user or --all")
            return
        
        # Get users to process
        if specific_user:
            # Try to get user by ID first, then by username
            try:
                user_id = int(specific_user)
                users = User.objects.filter(id=user_id)
            except ValueError:
                users = User.objects.filter(username=specific_user)
            
            if not users.exists():
                self.stderr.write(f"❌ User '{specific_user}' not found.")
                return
        else:
            users = User.objects.all()
        
        self.stdout.write(f"🔍 Processing {users.count()} users...")
        
        # Process each user
        for user in users:
            self.stdout.write(f"\n👤 Setting up defaults for user: {user.username}")
            
            # Ensure user has a profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(f"  ✅ Created user profile")
            
            # Set up default watchlist
            watchlists = Watchlist.objects.filter(user=user, is_default=True)
            
            if reset and watchlists.exists():
                watchlists.delete()
                self.stdout.write(f"  🔄 Reset default watchlist")
                watchlists = Watchlist.objects.none()
            
            if not watchlists.exists():
                with transaction.atomic():
                    # Create default watchlist
                    watchlist = Watchlist.objects.create(
                        user=user,
                        name="My Watchlist",
                        description="Default watchlist",
                        is_default=True
                    )
                    
                    # Add some default stocks (BIST30 stocks or a subset)
                    try:
                        # First try to get BIST30 stocks
                        bist30_stocks = Stock.objects.filter(indices__name='BIST30')[:10]
                        
                        # If that fails, get BIST100 stocks
                        if not bist30_stocks.exists():
                            bist30_stocks = Stock.objects.filter(indices__name='BIST100')[:10]
                        
                        # If that fails too, get any 10 stocks
                        if not bist30_stocks.exists():
                            bist30_stocks = Stock.objects.all()[:10]
                        
                        for stock in bist30_stocks:
                            watchlist.stocks.add(stock)
                        
                        self.stdout.write(f"  ✅ Created default watchlist with {bist30_stocks.count()} stocks")
                    
                    except Exception as e:
                        self.stderr.write(f"  ⚠️ Could not add default stocks to watchlist: {str(e)}")
            else:
                self.stdout.write(f"  ℹ️ User already has a default watchlist")
            
            # Set up default portfolio
            portfolios = Portfolio.objects.filter(user=user, is_default=True)
            
            if reset and portfolios.exists():
                portfolios.delete()
                self.stdout.write(f"  🔄 Reset default portfolio")
                portfolios = Portfolio.objects.none()
            
            if not portfolios.exists():
                portfolio = Portfolio.objects.create(
                    user=user,
                    name="My Portfolio",
                    description="Default investment portfolio",
                    currency="TRY",
                    is_default=True
                )
                self.stdout.write(f"  ✅ Created default portfolio")
            else:
                self.stdout.write(f"  ℹ️ User already has a default portfolio")
        
        self.stdout.write(self.style.SUCCESS("\n✅ User defaults setup completed!"))