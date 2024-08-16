#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable

# Initialize Redis connection
redis_store = redis.Redis()


def data_cacher(method: Callable[[str], str]) -> Callable[[str], str]:
    '''Caches the output of fetched data and tracks the request count.
    '''
    @wraps(method)
    def invoker(url: str) -> str:
        '''Wrapper function for caching and tracking.
        '''
        # Keys for the cache and access count
        cache_key = f'result:{url}'
        count_key = f'count:{url}'

        # Increment the access count
        redis_store.incr(count_key)

        # Check if the result is already cached
        cached_result = redis_store.get(cache_key)
        if cached_result:
            return cached_result.decode('utf-8')

        # Fetch the result, cache it, and set expiration
        result = method(url)
        redis_store.setex(cache_key, 10, result)
        return result

    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Fetches the content of a URL, caches the response, and tracks access.
    '''
    response = requests.get(url)
    response.raise_for_status()  # Ensure that any HTTP errors are raised
    return response.text
