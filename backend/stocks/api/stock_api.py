from rest_framework import generics
from ..models import Stock
from ..serializers import StockSerializer

class StockListAPIView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    
    def get_queryset(self):
        queryset = Stock.objects.all()
        index_name = self.request.query_params.get('index', None)
        if index_name:
            queryset = queryset.filter(indices__name=index_name)
        return queryset