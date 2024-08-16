#!/usr/bin/env python3
"""
This module provides a function to fetch and cache HTML page content
from a given URL using Redis. It also tracks the number of times each
URL is accessed.
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)
CACHE_EXPIRATION = 10  # Cache expiration time in seconds

def count_access(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator to count the number of accesses to a particular URL.

    Args:
        method: A function that fetches the page content from a URL.

    Returns:
        A wrapped function that increments the access count before calling
        the original function to get the content.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        redis_client.incr(count_key)  # Increment the access count
        return method(url)
    return wrapper

def cache_page(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator to cache the page content with an expiration time.

    Args:
        method: A function that fetches the page content from a URL.

    Returns:
        A wrapped function that either fetches the content from cache or
        calls the original function to get the content.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        cache_key = f"cache:{url}"
        cached_content = redis_client.get(cache_key)
        if cached_content:
            return cached_content.decode("utf-8")

        content = method(url)
        redis_client.setex(cache_key, CACHE_EXPIRATION, content)
        return content
    return wrapper

@count_access
@cache_page
def get_page(url: str) -> str:
    """
    Fetches the page content from the given URL and returns it.

    Args:
        url: The URL of the page to fetch.

    Returns:
        The HTML content of the page as a string.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text
