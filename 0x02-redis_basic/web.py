#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable


# Initialize the Redis connection
redis_store = redis.Redis(host='localhost', port=6379, db=0)
'''The module-level Redis instance.
'''


def data_cacher(method: Callable) -> Callable:
    '''Cache the output of fetched data.
    '''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output.
        '''
        # Increment the count of how many times this URL has been requested
        redis_store.incr(f'count:{url}')

        # Check if the result is already cached
        cached_result = redis_store.get(f'result:{url}')
        if cached_result:
            return cached_result.decode('utf-8')

        # Fetch the result and cache it
        result = method(url)
        redis_store.setex(f'result:{url}', 10, result)
        return result

    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    response = requests.get(url)
    response.raise_for_status()  # Exception for bad status codes
    return response.text
