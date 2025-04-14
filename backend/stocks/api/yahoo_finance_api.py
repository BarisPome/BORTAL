from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.yahoo_finance_service import YahooFinanceService

class StockDetailAPIView(APIView):
    """
    API view to fetch detailed stock information from Yahoo Finance
    """
    def get(self, request, symbol):
        try:
            service = YahooFinanceService()
            response_data = service.get_stock_detail(symbol)
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )