"""
Rate limiting module for EchoWrite AI

Provides in-memory rate limiting functionality with different tiers for demo and registered users.
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import threading


class RateLimiter:
    """
    In-memory rate limiter with user tier support
    
    Tracks requests per user with different limits for demo vs registered users.
    Automatically cleans up old request records to prevent memory leaks.
    """
    
    def __init__(self):
        # Thread-safe storage for user requests
        self._lock = threading.Lock()
        self.user_requests: Dict[str, List[datetime]] = defaultdict(list)
        
        # Rate limit configuration
        self.rate_limits = {
            "demo": {
                "requests_per_hour": 3,
                "requests_per_day": 5,
            },
            "registered": {
                "requests_per_hour": 15,
                "requests_per_day": 100,
            }
        }
        
        # Cache for cleanup optimization
        self._last_cleanup = datetime.now()
        self._cleanup_interval = timedelta(minutes=10)  # Clean up every 10 minutes
    
    def is_allowed(self, user_id: str, is_demo: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Check if user is allowed to make a request
        
        Args:
            user_id: Unique user identifier
            is_demo: Whether this is a demo user
            
        Returns:
            Tuple of (is_allowed, error_message)
            - (True, None) if request is allowed
            - (False, error_message) if rate limited
        """
        with self._lock:
            now = datetime.now()
            user_tier = "demo" if is_demo else "registered"
            limits = self.rate_limits[user_tier]
            
            # Get user's request history
            user_request_times = self.user_requests[user_id]
            
            # Clean up old requests for this user
            one_day_ago = now - timedelta(days=1)
            one_hour_ago = now - timedelta(hours=1)
            
            # Remove requests older than 1 day
            user_request_times[:] = [req_time for req_time in user_request_times if req_time > one_day_ago]
            
            # Check daily limit
            daily_requests = len(user_request_times)
            if daily_requests >= limits["requests_per_day"]:
                return False, f"Daily limit exceeded. Limit: {limits['requests_per_day']} requests per day. Try again tomorrow."
            
            # Check hourly limit
            hourly_requests = len([req_time for req_time in user_request_times if req_time > one_hour_ago])
            if hourly_requests >= limits["requests_per_hour"]:
                return False, f"Hourly limit exceeded. Limit: {limits['requests_per_hour']} requests per hour. Try again later."
            
            # Request is allowed - record it
            user_request_times.append(now)
            
            # Periodic cleanup
            if now - self._last_cleanup > self._cleanup_interval:
                self._cleanup_old_requests()
                self._last_cleanup = now
            
            return True, None
    
    def get_user_stats(self, user_id: str) -> Dict[str, int]:
        """
        Get current usage statistics for a user
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dictionary with current usage counts
        """
        with self._lock:
            now = datetime.now()
            user_request_times = self.user_requests[user_id]
            
            one_day_ago = now - timedelta(days=1)
            one_hour_ago = now - timedelta(hours=1)
            
            daily_count = len([req_time for req_time in user_request_times if req_time > one_day_ago])
            hourly_count = len([req_time for req_time in user_request_times if req_time > one_hour_ago])
            
            return {
                "requests_last_hour": hourly_count,
                "requests_last_day": daily_count,
                "total_requests": len(user_request_times)
            }
    
    def get_rate_limits_for_user(self, is_demo: bool = False) -> Dict[str, int]:
        """
        Get rate limit configuration for user tier
        
        Args:
            is_demo: Whether this is a demo user
            
        Returns:
            Dictionary with rate limits for the user tier
        """
        user_tier = "demo" if is_demo else "registered"
        return self.rate_limits[user_tier].copy()
    
    def _cleanup_old_requests(self):
        """
        Clean up old request records to prevent memory leaks
        
        Removes all requests older than 1 day and removes empty user records
        """
        cutoff_time = datetime.now() - timedelta(days=1)
        users_to_remove = []
        
        for user_id, request_times in self.user_requests.items():
            # Remove old requests
            request_times[:] = [req_time for req_time in request_times if req_time > cutoff_time]
            
            # Mark empty user records for removal
            if not request_times:
                users_to_remove.append(user_id)
        
        # Remove empty user records
        for user_id in users_to_remove:
            del self.user_requests[user_id]
    
    def reset_user_limits(self, user_id: str):
        """
        Reset rate limits for a specific user (admin function)
        
        Args:
            user_id: User to reset limits for
        """
        with self._lock:
            if user_id in self.user_requests:
                del self.user_requests[user_id]
    
    def get_system_stats(self) -> Dict[str, int]:
        """
        Get system-wide rate limiting statistics
        
        Returns:
            Dictionary with system statistics
        """
        with self._lock:
            total_users = len(self.user_requests)
            total_requests = sum(len(requests) for requests in self.user_requests.values())
            
            # Count active users (requests in last day)
            now = datetime.now()
            one_day_ago = now - timedelta(days=1)
            active_users = 0
            
            for request_times in self.user_requests.values():
                if any(req_time > one_day_ago for req_time in request_times):
                    active_users += 1
            
            return {
                "total_tracked_users": total_users,
                "total_requests_tracked": total_requests,
                "active_users_last_24h": active_users
            }