from django.db import models

from django.db import models

class Index(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    indices = models.ManyToManyField(Index, related_name="stocks", blank=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

