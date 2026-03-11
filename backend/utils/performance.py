"""
Performance Optimization Utilities
===================================
Caching, rate limiting, and performance monitoring.

Version: 1.0.0
"""

import time
from functools import wraps
from typing import Any, Optional, Callable
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class LRUCache:
    """Thread-safe LRU Cache for API responses"""
    
    def __init__(self, maxsize: int = 100, ttl: int = 300):
        """
        Args:
            maxsize: Maximum number of items in cache
            ttl: Time-to-live in seconds
        """
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: dict = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if not expired"""
        if key not in self.cache:
            return None
        
        # Check TTL
        if time.time() - self.timestamps[key] > self.ttl:
            self.delete(key)
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        """Set item in cache"""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.maxsize:
                # Remove oldest item
                oldest = next(iter(self.cache))
                self.delete(oldest)
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def delete(self, key: str):
        """Delete item from cache"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()
    
    def stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "ttl": self.ttl
        }


# Global cache instances
_api_cache = LRUCache(maxsize=200, ttl=60)  # 1 minute TTL
_heavy_cache = LRUCache(maxsize=50, ttl=300)  # 5 minutes TTL


def cached(ttl: int = 60, cache_key_fn: Callable = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds
        cache_key_fn: Function to generate cache key from args
    """
    def decorator(func):
        cache = LRUCache(maxsize=100, ttl=ttl)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_fn:
                key = cache_key_fn(*args, **kwargs)
            else:
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache.set(key, result)
            return result
        
        # Attach cache for inspection
        wrapper.cache = cache
        return wrapper
    
    return decorator


def timed(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        
        if elapsed > 1.0:  # Log slow operations
            logger.warning(f"Slow operation: {func.__name__} took {elapsed:.2f}s")
        
        return result
    return wrapper


class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Clean old entries
        if key in self.requests:
            self.requests[key] = [
                t for t in self.requests[key] 
                if now - t < self.window_seconds
            ]
        else:
            self.requests[key] = []
        
        # Check limit
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        # Record request
        self.requests[key].append(now)
        return True
    
    def remaining(self, key: str) -> int:
        """Get remaining requests for key"""
        now = time.time()
        if key not in self.requests:
            return self.max_requests
        
        valid_requests = [
            t for t in self.requests[key]
            if now - t < self.window_seconds
        ]
        return max(0, self.max_requests - len(valid_requests))


# Global rate limiters
api_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
ai_rate_limiter = RateLimiter(max_requests=20, window_seconds=60)


def get_cache_stats() -> dict:
    """Get all cache statistics"""
    return {
        "api_cache": _api_cache.stats(),
        "heavy_cache": _heavy_cache.stats()
    }


def clear_all_caches():
    """Clear all caches"""
    _api_cache.clear()
    _heavy_cache.clear()
