#!/usr/bin/env python3
"""
This module provides a function to fetch and cache HTML page content
from a given URL using Redis. It also tracks the number of times each
URL is accessed.
"""

import requests
import redis
from functools import wraps

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)
CACHE_EXPIRATION = 10  # Cache expiration time in seconds


def cache_page(method):
    """
    Decorator to cache the page content with an expiration time.
    """
    @wraps(method)
    def wrapper(url):
        cache_key = f"cache:{url}"
        cached_content = redis_client.get(cache_key)
        if cached_content:
            return cached_content.decode("utf-8")

        content = method(url)
        redis_client.setex(cache_key, CACHE_EXPIRATION, content)
        return content
    return wrapper


def count_access(method):
    """
    Decorator to count the number of accesses to a particular URL.
    """
    @wraps(method)
    def wrapper(url):
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(url)
    return wrapper


@count_access
@cache_page
def get_page(url):
    """
    Fetches the page content from the given URL and returns it.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text
