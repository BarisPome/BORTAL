# Generated by Django 5.2 on 2025-04-15 10:06

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Index',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('display_name', models.CharField(default='', max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('region', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('source', models.CharField(max_length=100)),
                ('url', models.URLField(blank=True, max_length=255, null=True)),
                ('image_url', models.URLField(blank=True, max_length=255, null=True)),
                ('publication_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'News',
            },
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('display_name', models.CharField(default='', max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SystemSetting',
            fields=[
                ('key', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('value', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('currency', models.CharField(default='TRY', max_length=10)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolios', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('symbol', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('exchange', models.CharField(blank=True, max_length=50, null=True)),
                ('currency', models.CharField(blank=True, max_length=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stocks', to='stocks.sector')),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_type', models.CharField(choices=[('buy', 'Buy'), ('sell', 'Sell'), ('dividend', 'Dividend')], max_length=10)),
                ('transaction_date', models.DateTimeField()),
                ('quantity', models.DecimalField(decimal_places=6, max_digits=14)),
                ('price_per_unit', models.DecimalField(decimal_places=4, max_digits=12)),
                ('fees', models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='stocks.portfolio')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
            ],
        ),
        migrations.CreateModel(
            name='NewsStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.news')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
            ],
            options={
                'unique_together': {('news', 'stock')},
            },
        ),
        migrations.AddField(
            model_name='news',
            name='stocks',
            field=models.ManyToManyField(related_name='news', through='stocks.NewsStock', to='stocks.stock'),
        ),
        migrations.CreateModel(
            name='FinancialReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('report_type', models.CharField(choices=[('annual', 'Annual'), ('quarterly', 'Quarterly')], max_length=20)),
                ('fiscal_year', models.IntegerField()),
                ('fiscal_quarter', models.IntegerField(blank=True, null=True)),
                ('publication_date', models.DateField()),
                ('period_start_date', models.DateField()),
                ('period_end_date', models.DateField()),
                ('currency', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='financial_reports', to='stocks.stock')),
            ],
            options={
                'unique_together': {('stock', 'report_type', 'fiscal_year', 'fiscal_quarter')},
            },
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('alert_type', models.CharField(choices=[('price', 'Price'), ('volume', 'Volume'), ('technical', 'Technical'), ('news', 'News')], max_length=20)),
                ('condition', models.CharField(choices=[('above', 'Above'), ('below', 'Below'), ('percent_change', 'Percent Change'), ('cross_above', 'Cross Above'), ('cross_below', 'Cross Below')], max_length=20)),
                ('value', models.DecimalField(decimal_places=4, max_digits=12)),
                ('is_active', models.BooleanField(default=True)),
                ('is_triggered', models.BooleanField(default=False)),
                ('last_triggered', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to=settings.AUTH_USER_MODEL)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='stocks.stock')),
            ],
        ),
        migrations.CreateModel(
            name='StockIndex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('index', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.index')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
            ],
            options={
                'unique_together': {('stock', 'index')},
            },
        ),
        migrations.AddField(
            model_name='stock',
            name='indices',
            field=models.ManyToManyField(related_name='stocks', through='stocks.StockIndex', to='stocks.index'),
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('view', 'View'), ('search', 'Search'), ('analysis', 'Analysis'), ('trade', 'Trade')], max_length=50)),
                ('resource_type', models.CharField(blank=True, choices=[('stock', 'Stock'), ('index', 'Index'), ('watchlist', 'Watchlist'), ('portfolio', 'Portfolio')], max_length=50, null=True)),
                ('resource_id', models.UUIDField(blank=True, null=True)),
                ('details', models.JSONField(blank=True, null=True)),
                ('ip_address', models.CharField(blank=True, max_length=45, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User Activities',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watchlists', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WatchlistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
                ('watchlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.watchlist')),
            ],
            options={
                'unique_together': {('watchlist', 'stock')},
            },
        ),
        migrations.AddField(
            model_name='watchlist',
            name='stocks',
            field=models.ManyToManyField(related_name='watchlists', through='stocks.WatchlistItem', to='stocks.stock'),
        ),
        migrations.CreateModel(
            name='FinancialReportItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('item_value', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('item_type', models.CharField(choices=[('asset', 'Asset'), ('liability', 'Liability'), ('equity', 'Equity'), ('revenue', 'Revenue'), ('expense', 'Expense')], max_length=50)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='stocks.financialreport')),
            ],
            options={
                'unique_together': {('report', 'item_name')},
            },
        ),
        migrations.CreateModel(
            name='IndexPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('open', models.DecimalField(decimal_places=4, max_digits=12)),
                ('high', models.DecimalField(decimal_places=4, max_digits=12)),
                ('low', models.DecimalField(decimal_places=4, max_digits=12)),
                ('close', models.DecimalField(decimal_places=4, max_digits=12)),
                ('volume', models.BigIntegerField()),
                ('index', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='stocks.index')),
            ],
            options={
                'unique_together': {('index', 'date')},
            },
        ),
        migrations.CreateModel(
            name='PortfolioHolding',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity', models.DecimalField(decimal_places=6, max_digits=14)),
                ('average_cost', models.DecimalField(decimal_places=4, max_digits=12)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='holdings', to='stocks.portfolio')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
            ],
            options={
                'unique_together': {('portfolio', 'stock')},
            },
        ),
        migrations.CreateModel(
            name='MLPrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=50)),
                ('prediction_date', models.DateField()),
                ('target_date', models.DateField()),
                ('predicted_value', models.DecimalField(decimal_places=4, max_digits=12)),
                ('confidence', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('actual_value', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('error_margin', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictions', to='stocks.stock')),
            ],
            options={
                'unique_together': {('stock', 'model_name', 'prediction_date', 'target_date')},
            },
        ),
        migrations.CreateModel(
            name='StockFundamental',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('market_cap', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('pe_ratio', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('eps', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('dividend_yield', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('price_to_book', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('price_to_sales', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('debt_to_equity', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('roe', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('roa', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('revenue', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('net_income', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('gross_margin', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('operating_margin', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('profit_margin', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('free_cash_flow', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fundamentals', to='stocks.stock')),
            ],
            options={
                'unique_together': {('stock', 'date')},
            },
        ),
        migrations.CreateModel(
            name='StockPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('open', models.DecimalField(decimal_places=4, max_digits=12)),
                ('high', models.DecimalField(decimal_places=4, max_digits=12)),
                ('low', models.DecimalField(decimal_places=4, max_digits=12)),
                ('close', models.DecimalField(decimal_places=4, max_digits=12)),
                ('adjusted_close', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('volume', models.BigIntegerField()),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='stocks.stock')),
            ],
            options={
                'indexes': [models.Index(fields=['stock', 'date'], name='stocks_stoc_stock_i_86bebf_idx')],
                'unique_together': {('stock', 'date')},
            },
        ),
        migrations.CreateModel(
            name='TechnicalIndicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('rsi_14', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('macd', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('macd_signal', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('macd_histogram', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('stochastic_k', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('stochastic_d', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('cci_14', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('atr_14', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('bollinger_upper', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('bollinger_middle', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('bollinger_lower', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('ma_5', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('ma_10', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('ma_20', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('ma_50', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('ma_100', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('ma_200', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='technical_indicators', to='stocks.stock')),
            ],
            options={
                'unique_together': {('stock', 'date')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='watchlist',
            unique_together={('user', 'name')},
        ),
    ]
