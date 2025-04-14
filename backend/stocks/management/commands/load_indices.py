import os
import json
from django.core.management.base import BaseCommand
from stocks.models import Stock, Index
from django.conf import settings

class Command(BaseCommand):
    help = "Load stock indices from a JSON file"

    def handle(self, *args, **kwargs):
        data_path = os.path.join(settings.BASE_DIR, 'data')
        json_path = os.path.join(data_path, 'Endeksler.json')

        try:
            with open(json_path, 'r') as file:
                indices_data = json.load(file)
        except FileNotFoundError:
            self.stderr.write("❌ Error: 'indices.json' not found in /data directory.")
            return
        except json.JSONDecodeError as e:
            self.stderr.write(f"❌ Error decoding JSON: {e}")
            return
        except Exception as e:
            self.stderr.write(f"❌ Error reading JSON file: {e}")
            return

        # Process each index and its stocks
        for index_name, stock_symbols in indices_data.items():
            # Create or get the index
            index, created = Index.objects.get_or_create(name=index_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created index: {index_name}'))
            else:
                self.stdout.write(f'🔄 Using existing index: {index_name}')
            
            # Add stocks to the index
            added_count = 0
            not_found_count = 0
            
            for symbol in stock_symbols:
                try:
                    stock = Stock.objects.get(symbol=symbol)
                    stock.indices.add(index)
                    added_count += 1
                except Stock.DoesNotExist:
                    self.stderr.write(f"⚠️ Stock with symbol '{symbol}' not found, skipping")
                    not_found_count += 1
            
            self.stdout.write(f'📊 Added {added_count} stocks to {index_name} index')
            if not_found_count > 0:
                self.stdout.write(f'⚠️ {not_found_count} stocks from {index_name} index were not found in the database')