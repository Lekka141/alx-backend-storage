#!/usr/bin/env python3
'''A module with tools for request caching and tracking.'''

import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
'''The module-level Redis instance.'''


def data_cacher(method: Callable[[str], str]) -> Callable[[str], str]:
    '''Caches the output of fetched data.

    Args:
        method (Callable[[str], str]): The function that fetches the data.

    Returns:
        Callable[[str], str]: The wrapped function that caches its result.
    '''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output.

        Args:
            url (str): The URL to fetch the content from.

        Returns:
            str: The content of the URL, either cached or freshly fetched.
        '''
        # Increment the access count for the URL
        redis_store.incr(f'count:{url}')

        # Check if the URL result is cached
        cached_result = redis_store.get(f'result:{url}')
        if cached_result:
            return cached_result.decode('utf-8')

        # Fetch the result and cache it with an expiration time
        result = method(url)
        redis_store.setex(f'result:{url}', 10, result)
        return result

    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response
    and tracking the request.

    Args:
        url (str): The URL to fetch the content from.

    Returns:
        str: The content of the URL.
    '''
    return requests.get(url).text
