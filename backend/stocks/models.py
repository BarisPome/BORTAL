from django.db import models
import uuid
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class Index(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100, default="")
    description = models.TextField(blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.display_name or self.name


class Sector(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100, default="")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.display_name or self.name


class Stock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True, related_name='stocks')
    description = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    exchange = models.CharField(max_length=50, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    indices = models.ManyToManyField(Index, through='StockIndex', related_name='stocks')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"


class StockIndex(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    index = models.ForeignKey(Index, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('stock', 'index')


class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    open = models.DecimalField(max_digits=12, decimal_places=4)
    high = models.DecimalField(max_digits=12, decimal_places=4)
    low = models.DecimalField(max_digits=12, decimal_places=4)
    close = models.DecimalField(max_digits=12, decimal_places=4)
    adjusted_close = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    volume = models.BigIntegerField()
    
    class Meta:
        unique_together = ('stock', 'date')
        indexes = [
            models.Index(fields=['stock', 'date']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.date} - {self.close}"


class IndexPrice(models.Model):
    index = models.ForeignKey(Index, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    open = models.DecimalField(max_digits=12, decimal_places=4)
    high = models.DecimalField(max_digits=12, decimal_places=4)
    low = models.DecimalField(max_digits=12, decimal_places=4)
    close = models.DecimalField(max_digits=12, decimal_places=4)
    volume = models.BigIntegerField()
    
    class Meta:
        unique_together = ('index', 'date')
    
    def __str__(self):
        return f"{self.index.name} - {self.date} - {self.close}"


class StockFundamental(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='fundamentals')
    date = models.DateField()
    market_cap = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    eps = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    dividend_yield = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    price_to_book = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    price_to_sales = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    roe = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    roa = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    revenue = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    net_income = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    gross_margin = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    operating_margin = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    profit_margin = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    free_cash_flow = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    
    class Meta:
        unique_together = ('stock', 'date')
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.date} - Fundamentals"


class FinancialReport(models.Model):
    REPORT_TYPES = [
        ('annual', 'Annual'),
        ('quarterly', 'Quarterly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='financial_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    fiscal_year = models.IntegerField()
    fiscal_quarter = models.IntegerField(blank=True, null=True)
    publication_date = models.DateField()
    period_start_date = models.DateField()
    period_end_date = models.DateField()
    currency = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        unique_together = ('stock', 'report_type', 'fiscal_year', 'fiscal_quarter')
    
    def __str__(self):
        quarter = f"Q{self.fiscal_quarter}" if self.fiscal_quarter else "Annual"
        return f"{self.stock.symbol} - {self.fiscal_year} {quarter} Report"


class FinancialReportItem(models.Model):
    ITEM_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    report = models.ForeignKey(FinancialReport, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=100)
    item_value = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    item_type = models.CharField(max_length=50, choices=ITEM_TYPES)
    
    class Meta:
        unique_together = ('report', 'item_name')
    
    def __str__(self):
        return f"{self.report} - {self.item_name}: {self.item_value}"


class TechnicalIndicator(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='technical_indicators')
    date = models.DateField()
    rsi_14 = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    macd = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    macd_signal = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    macd_histogram = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    stochastic_k = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    stochastic_d = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    cci_14 = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    atr_14 = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    bollinger_upper = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    bollinger_middle = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    bollinger_lower = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    ma_5 = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    ma_10 = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    ma_20 = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    ma_50 = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    ma_100 = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    ma_200 = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    
    class Meta:
        unique_together = ('stock', 'date')
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.date} - Technical Indicators"


class News(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    source = models.CharField(max_length=100)
    url = models.URLField(max_length=255, blank=True, null=True)
    image_url = models.URLField(max_length=255, blank=True, null=True)
    publication_date = models.DateTimeField()
    stocks = models.ManyToManyField(Stock, through='NewsStock', related_name='news')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        verbose_name_plural = 'News'
    
    def __str__(self):
        return self.title


class NewsStock(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('news', 'stock')


class Watchlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    stocks = models.ManyToManyField(Stock, through='WatchlistItem', related_name='watchlists')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        unique_together = ('user', 'name')
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class WatchlistItem(models.Model):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('watchlist', 'stock')


class Portfolio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=10, default='TRY')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        unique_together = ('user', 'name')
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PortfolioTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('dividend', 'Dividend'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    transaction_date = models.DateTimeField()
    quantity = models.DecimalField(max_digits=14, decimal_places=6)
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=4)
    fees = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.transaction_type} {self.quantity} {self.stock.symbol}"


class PortfolioHolding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=14, decimal_places=6)
    average_cost = models.DecimalField(max_digits=12, decimal_places=4)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('portfolio', 'stock')
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.quantity} {self.stock.symbol}"


class MLPrediction(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='predictions')
    model_name = models.CharField(max_length=50)
    prediction_date = models.DateField()
    target_date = models.DateField()
    predicted_value = models.DecimalField(max_digits=12, decimal_places=4)
    confidence = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    actual_value = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    error_margin = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        unique_together = ('stock', 'model_name', 'prediction_date', 'target_date')
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.model_name} - {self.prediction_date} to {self.target_date}"


class Alert(models.Model):
    ALERT_TYPES = [
        ('price', 'Price'),
        ('volume', 'Volume'),
        ('technical', 'Technical'),
        ('news', 'News'),
    ]
    
    CONDITION_TYPES = [
        ('above', 'Above'),
        ('below', 'Below'),
        ('percent_change', 'Percent Change'),
        ('cross_above', 'Cross Above'),
        ('cross_below', 'Cross Below'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    condition = models.CharField(max_length=20, choices=CONDITION_TYPES)
    value = models.DecimalField(max_digits=12, decimal_places=4)
    is_active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    last_triggered = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol} {self.alert_type} {self.condition} {self.value}"


class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('view', 'View'),
        ('search', 'Search'),
        ('analysis', 'Analysis'),
        ('trade', 'Trade'),
    ]
    
    RESOURCE_TYPES = [
        ('stock', 'Stock'),
        ('index', 'Index'),
        ('watchlist', 'Watchlist'),
        ('portfolio', 'Portfolio'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES, blank=True, null=True)
    resource_id = models.UUIDField(blank=True, null=True)
    details = models.JSONField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_at}"


class SystemSetting(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.key