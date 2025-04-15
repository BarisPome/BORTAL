import os
import re
import json
import requests
import yfinance as yf
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from stocks.models import Stock, News, NewsStock


class Command(BaseCommand):
    help = "Fetch financial news for BIST stocks"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Fetch news from the past N days (default: 7)'
        )
        parser.add_argument(
            '--symbol',
            type=str,
            help='Fetch news for a specific stock symbol only'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum number of news articles to fetch per stock (default: 20)'
        )

    def handle(self, *args, **options):
        days = options['days']
        specific_symbol = options.get('symbol')
        limit = options.get('limit', 20)
        
        # Get stocks to process
        if specific_symbol:
            stocks = Stock.objects.filter(symbol=specific_symbol)
            if not stocks.exists():
                self.stderr.write(f"❌ Stock with symbol '{specific_symbol}' not found.")
                return
        else:
            # Focus on stocks in the BIST100 index for news to avoid processing too many
            try:
                bist100 = Stock.objects.filter(indices__name='BIST100')
                if bist100.exists():
                    stocks = bist100
                    self.stdout.write(f"🔍 Fetching news for {stocks.count()} BIST100 stocks")
                else:
                    # Fallback to all active stocks
                    stocks = Stock.objects.filter(is_active=True)
                    self.stdout.write(f"⚠️ BIST100 index not found, fetching news for all {stocks.count()} active stocks")
            except Exception:
                # Fallback to all active stocks
                stocks = Stock.objects.filter(is_active=True)
                self.stdout.write(f"⚠️ BIST100 index not found, fetching news for all {stocks.count()} active stocks")
        
        # Calculate the date from which to fetch news
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for stock in stocks:
            self.stdout.write(f"\n📰 Fetching news for {stock.symbol} - {stock.name}")
            
            # Use yfinance to get news
            try:
                # For Turkish stocks, append '.IS' to the symbol for Yahoo Finance
                yahoo_symbol = f"{stock.symbol}.IS"
                
                yf_stock = yf.Ticker(yahoo_symbol)
                news_items = yf_stock.news
                
                if not news_items:
                    self.stdout.write(f"  ℹ️ No news found for {stock.symbol}")
                    continue
                
                # Process news items
                count_added = 0
                for item in news_items[:limit]:  # Limit the number of news items per stock
                    # Extract data from the news item
                    title = item.get('title', '').strip()
                    if not title:  # Skip items without a title
                        continue
                    
                    # Parse the timestamp (usually in Unix epoch format)
                    try:
                        if 'providerPublishTime' in item:
                            pub_time = datetime.fromtimestamp(item['providerPublishTime'])
                        else:
                            # Skip if we don't have a publication time
                            continue
                    except Exception:
                        # Skip if we can't parse the time
                        continue
                    
                    # Skip news older than our cutoff date
                    if pub_time < cutoff_date:
                        continue
                    
                    # Extract other news data
                    url = item.get('link', '')
                    source = item.get('publisher', '')
                    if isinstance(source, dict):
                        source = source.get('name', 'Unknown')
                    
                    # Get content/summary
                    content = item.get('summary', '')
                    if not content:
                        content = title  # Use title as content if no summary
                    
                    # Get image URL if available
                    image_url = None
                    if 'thumbnail' in item and isinstance(item['thumbnail'], dict):
                        image_url = item['thumbnail'].get('resolutions', [{}])[0].get('url', None)
                    
                    # Create or update news record
                    news, created = News.objects.update_or_create(
                        title=title,
                        publication_date=pub_time,
                        defaults={
                            'content': content,
                            'source': source or 'Yahoo Finance',
                            'url': url,
                            'image_url': image_url,
                        }
                    )
                    
                    # Associate the news with the stock
                    NewsStock.objects.get_or_create(news=news, stock=stock)
                    
                    if created:
                        count_added += 1
                
                self.stdout.write(f"  ✅ Added {count_added} new articles for {stock.symbol}")
                
            except Exception as e:
                self.stderr.write(f"  ❌ Error fetching news for {stock.symbol}: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS("\n✅ News fetching completed!"))


    def _clean_html(self, text):
        """Remove HTML tags from text"""
        if not text:
            return ""
        cleanr = re.compile('<.*?>')
        text = re.sub(cleanr, '', text)
        return text.strip()