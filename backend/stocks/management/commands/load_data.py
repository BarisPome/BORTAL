#/Users/barispome/Desktop/Project/BORTAL/backend/stocks/management/commands/load_data.py

import os
from django.core.management.base import BaseCommand
from stocks.models import Stock
from django.conf import settings
import pandas as pd

class Command(BaseCommand):
    help = "Load stocks from 'Şirketler.csv' in the data folder (only ticker and name)"

    def handle(self, *args, **kwargs):
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

        for _, row in df.iterrows():
            symbol = str(row['ticker']).strip()
            name = str(row['name']).strip()

            stock, created = Stock.objects.get_or_create(
                symbol=symbol,
                defaults={'name': name}
            )

            if not created:
                stock.name = name
                stock.save()
                self.stdout.write(f'🔄 Updated: {symbol} - {name}')
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ Created: {symbol} - {name}'))
