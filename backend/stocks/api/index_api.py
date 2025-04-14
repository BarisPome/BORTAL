from rest_framework import generics
from ..models import Index
from ..serializers import IndexSerializer, IndexDetailSerializer

class IndexListAPIView(generics.ListAPIView):
    queryset = Index.objects.all()
    serializer_class = IndexSerializer

class IndexDetailAPIView(generics.RetrieveAPIView):
    queryset = Index.objects.all()
    serializer_class = IndexDetailSerializer
    lookup_field = 'name'