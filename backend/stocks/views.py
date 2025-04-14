from rest_framework import generics
from .models import Stock, Index
from .serializers import StockSerializer, IndexSerializer, IndexDetailSerializer

# API views
class IndexListAPIView(generics.ListAPIView):
    queryset = Index.objects.all()
    serializer_class = IndexSerializer

class IndexDetailAPIView(generics.RetrieveAPIView):
    queryset = Index.objects.all()
    serializer_class = IndexDetailSerializer
    lookup_field = 'name'

class StockListAPIView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    
    def get_queryset(self):
        queryset = Stock.objects.all()
        index_name = self.request.query_params.get('index', None)
        if index_name:
            queryset = queryset.filter(indices__name=index_name)
        return queryset