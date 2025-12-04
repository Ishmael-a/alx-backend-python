import logging
from datetime import datetime
from django.http import HttpResponseForbidden
from collections import defaultdict
import time

# Configure logging for request logging
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('requests.log')
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class RequestLoggingMiddleware:
    """
    Middleware that logs each user's requests to a file.
    Logs: timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        print("Middleware is running!")
        # Get user information
        user = request.user if request.user.is_authenticated else "Anonymous"
        
        # Log the request
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        print(f"Log Message!:: {log_message}")
        logger.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the messaging app during certain hours.
    Access is denied outside 9 AM to 6 PM.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get current hour
        current_hour = datetime.now().hour
        
        # Check if current time is outside 9 AM (9) to 6 PM (18)
        if current_hour < 9 or current_hour >= 18:
            return HttpResponseForbidden(
                "Access to the chat is restricted outside of 9 AM to 6 PM."
            )
        
        # Process the request if within allowed time
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    """
    Middleware that limits the number of chat messages a user can send
    within a certain time window based on their IP address.
    Limit: 5 messages per minute.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Store message counts per IP address
        self.ip_message_counts = defaultdict(list)
        self.message_limit = 5
        self.time_window = 60  # 60 seconds (1 minute)
    
    def __call__(self, request):
        # Only check POST requests (messages)
        if request.method == 'POST':
            # Get client IP address
            ip_address = self.get_client_ip(request)
            current_time = time.time()
            
            # Clean old timestamps outside the time window
            self.ip_message_counts[ip_address] = [
                timestamp for timestamp in self.ip_message_counts[ip_address]
                if current_time - timestamp < self.time_window
            ]
            
            # Check if user has exceeded the limit
            if len(self.ip_message_counts[ip_address]) >= self.message_limit:
                return HttpResponseForbidden(
                    f"Rate limit exceeded. You can only send {self.message_limit} messages per minute."
                )
            
            # Add current timestamp
            self.ip_message_counts[ip_address].append(current_time)
        
        # Process the request
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolePermissionMiddleware:
    """
    Middleware that checks the user's role before allowing access to specific actions.
    Only admin or moderator roles are allowed access.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Get user's role from the User model (your model has role field)
            user_role = request.user.role
            
            # Check if user is admin or moderator
            # Also allow superusers by default
            if not (request.user.is_superuser or 
                    user_role in ['admin', 'moderator']):
                return HttpResponseForbidden(
                    "You do not have permission to access this resource. "
                    "Admin or moderator role required."
                )
        
        # Process the request
        response = self.get_response(request)
        return response