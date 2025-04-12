import os
from django.core.management.base import BaseCommand
from stocks.models import Stock, Index
from django.conf import settings
import pandas as pd

class Command(BaseCommand):
    help = 'Load indices and stocks from Excel files'

    def handle(self, *args, **kwargs):
        data_path = os.path.join(settings.BASE_DIR, 'data')

        # Load indices.xlsx
        indices_path = os.path.join(data_path, 'indices.xlsx')
        indices_df = pd.read_excel(indices_path)

        for name in indices_df['name'].dropna():
            index, created = Index.objects.get_or_create(name=name.strip())
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created index: {name}'))

        # Load stocks.xlsx
        stocks_path = os.path.join(data_path, 'stocks.xlsx')
        stocks_df = pd.read_excel(stocks_path)

        for _, row in stocks_df.iterrows():
            symbol = row['symbol'].strip()
            name = row['name'].strip()
            index_names = row['indices'].split('|')

            stock, created = Stock.objects.get_or_create(symbol=symbol, name=name)
            for index_name in index_names:
                index_name = index_name.strip()
                index = Index.objects.get(name=index_name)
                stock.indices.add(index)

            stock.save()
            self.stdout.write(self.style.SUCCESS(f'Added stock: {symbol}'))
