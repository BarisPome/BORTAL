from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

class BaseAPIView(APIView):
    """
    Base API view class providing common functionality for BORTAL API endpoints.
    
    Features:
    - Standardized response format
    - Error handling and logging
    - Optional caching
    - Transaction support
    """
    
    # Set to True to enforce authentication
    authentication_required = False
    
    # Cache timeout in seconds (None = no caching)
    cache_timeout = None
    
    # Set to True to use atomic transactions
    use_transactions = False
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add caching and permissions"""
        # Apply caching if configured
        if self.cache_timeout is not None and request.method.lower() == 'get':
            decorator = method_decorator(cache_page(self.cache_timeout))
            # Vary cache by cookie (user) if authentication is required
            if self.authentication_required:
                decorator = method_decorator(vary_on_cookie(cache_page(self.cache_timeout)))
            view = decorator(super().dispatch)
        else:
            view = super().dispatch
        
        return view(request, *args, **kwargs)
    
    def initial(self, request, *args, **kwargs):
        """Handle authentication requirements"""
        super().initial(request, *args, **kwargs)
        if self.authentication_required and not request.user.is_authenticated:
            self.permission_denied(request)
    
    def handle_exception(self, exc):
        """Global exception handler for API views"""
        if isinstance(exc, Http404):
            return self.error_response(
                f"Resource not found: {str(exc)}",
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Log unexpected errors
        logger.exception("API error occurred")
        
        # Return friendly error message
        return self.error_response(
            "An unexpected error occurred. Please try again later.",
            error_code="server_error",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def success_response(self, data=None, message=None, status=status.HTTP_200_OK, **extra):
        """
        Standard success response format.
        
        Args:
            data: The response data
            message: Optional success message
            status: HTTP status code
            extra: Any additional fields to include in the response
        """
        response = {
            "status": "success",
            "data": data if data is not None else {},
        }
        
        if message:
            response["message"] = message
            
        # Add any extra fields
        response.update(extra)
        
        return Response(response, status=status)
    
    def error_response(self, message, error_code=None, errors=None, status=status.HTTP_400_BAD_REQUEST, **extra):
        """
        Standard error response format.
        
        Args:
            message: Error message
            error_code: Optional error code identifier
            errors: Optional dict of field-specific errors
            status: HTTP status code
            extra: Any additional fields to include in the response
        """
        response = {
            "status": "error",
            "message": message,
        }
        
        if error_code:
            response["error_code"] = error_code
            
        if errors:
            response["errors"] = errors
            
        # Add any extra fields
        response.update(extra)
        
        return Response(response, status=status)
    
    def get(self, request, *args, **kwargs):
        """Default GET method - must be overridden"""
        return self.error_response("Method not implemented", status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def post(self, request, *args, **kwargs):
        """Default POST method - must be overridden"""
        return self.error_response("Method not implemented", status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def put(self, request, *args, **kwargs):
        """Default PUT method - must be overridden"""
        return self.error_response("Method not implemented", status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def patch(self, request, *args, **kwargs):
        """Default PATCH method - must be overridden"""
        return self.error_response("Method not implemented", status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def delete(self, request, *args, **kwargs):
        """Default DELETE method - must be overridden"""
        return self.error_response("Method not implemented", status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def perform_operation(self, operation, *args, **kwargs):
        """
        Perform an operation within a transaction if use_transactions is True.
        
        Args:
            operation: Function to execute
            args, kwargs: Arguments to pass to the operation function
        
        Returns:
            The result of the operation function
        """
        if self.use_transactions:
            with transaction.atomic():
                return operation(*args, **kwargs)
        else:
            return operation(*args, **kwargs)
            
    @classmethod
    def with_authentication(cls):
        """Create a subclass that requires authentication"""
        return type(f'Authenticated{cls.__name__}', (cls,), {'authentication_required': True})
    
    @classmethod
    def with_cache(cls, timeout=60):
        """Create a subclass with caching enabled"""
        return type(f'Cached{cls.__name__}', (cls,), {'cache_timeout': timeout})