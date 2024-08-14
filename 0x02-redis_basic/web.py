#!/usr/bin/env python3
"""
This module provides a function to fetch and cache HTML page content from a
given URL using Redis. It also tracks the number of times each URL is accessed.
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis connection
redis_client = redis.Redis()
CACHE_EXPIRATION = 10  # Cache expiration time in seconds


def cache_page(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator to cache the page content with an expiration time.

    Args:
        method: A function that fetches the page content from a URL.

    Returns:
        A wrapped function that either fetches the content from cache or calls
        the original function to get the content.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        cache_key = f"cache:{url}"
        if redis_client.exists(cache_key):
            return redis_client.get(cache_key).decode("utf-8")

        content = method(url)
        redis_client.setex(cache_key, CACHE_EXPIRATION, content)
        return content
    return wrapper


def count_access(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator to count the number of accesses to a particular URL.

    Args:
        method: A function that fetches the page content from a URL.

    Returns:
        A wrapped function that increments the access count before calling the
        original function to get the content.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(url)
    return wrapper


@cache_page
@count_access
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
