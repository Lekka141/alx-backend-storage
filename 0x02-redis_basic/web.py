#!/usr/bin/env python3
import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis connection
redis_client = redis.Redis()
CACHE_EXPIRATION = 10  # Cache expiration time in seconds

def cache_page(method: Callable) -> Callable:
    """Decorator to cache the page content with an expiration time."""
    @wraps(method)
    def wrapper(url: str) -> str:
        cache_key = f"cache:{url}"
        if redis_client.exists(cache_key):
            return redis_client.get(cache_key).decode("utf-8")

        content = method(url)
        redis_client.setex(cache_key, CACHE_EXPIRATION, content)
        return content
    return wrapper

def count_access(method: Callable) -> Callable:
    """Decorator to count the number of accesses to a particular URL."""
    @wraps(method)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(url)
    return wrapper

@cache_page
@count_access
def get_page(url: str) -> str:
    """Fetches the page content from the given URL and returns it."""
    response = requests.get(url)
    return response.text
