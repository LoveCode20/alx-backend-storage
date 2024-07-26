#!/usr/bin/env python3
"""Declares redis class and other methods"""

import redis  # Importing the Redis Python client
from uuid import uuid4  # Importing uuid4 function to generate UUIDs
from typing import Union, Callable, Optional  # Importing type hints
from functools import wraps  # Importing wraps decorator to preserve metadata


def count_calls(method: Callable) -> Callable:
    '''Counts times Cache is called'''
    key = method.__qualname__  # Extracting the method name

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''wrapps the method and returns wrapper'''
        self._redis.incr(key)  # Incrementing the call count in Redis
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    '''Decorator that stores inputs and outputs'''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''wrapps the method and returns wrapper'''
        input = str(args)  # Converting arguments to string
        # Storing input in Redis
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        out_put = str(method(self, *args, **kwargs))  # Executing the method
        # Storing output in Redis
        self._redis.rpush(method.__qualname__ + ":outputs", out_put)
        return out_put
    return wrapper


def replay(fn: Callable):
    '''definition that displays the calls'''
    red = redis.Redis()  # Connecting to Redis
    func_name = fn.__qualname__  # Extracting function name
    gett = red.get(func_name)  # Getting call count from Redis
    try:
        gett = int(c.decode("utf-8"))  # Decoding call count
    except Exception:
        gett = 0  # Setting default count to 0 if not found
    print("{} was called {} times:".format(func_name, c))
    # Printing function name and call count
    in_puts = r.lrange("{}:inputs".format(func_name), 0, -1)
    # Getting inputs from Redis
    out_puts = r.lrange("{}:outputs".format(func_name), 0, -1)
    # Getting outputs from Redis
    for inputs, outputs in zip(in_puts, out_puts):
        try:
            inputs = inputs.decode("utf-8")  # Decoding input
        except Exception:
            inputs = ""  # Handling decoding errors
        try:
            outputs = outputs.decode("utf-8")  # Decoding output
        except Exception:
            outputs = ""  # Handling decoding errors
        print("{}(*{}) -> {}".format(func_name, inp, outp))
        # Printing function call history


class Cache:
    '''Interacts with the redis database'''
    def __init__(self):
        '''Interacts and flushes the redis database'''
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        # Connecting to Redis
        self._redis.flushdb()
        # Flushing the Redis database upon initialization

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''stores data and returns a unique key'''
        key_uniq = str(uuid4())  # Generating a unique key
        self._redis.set(key_uniq, data)  # Storing data in Redis
        return key_uniq  # Returning the unique key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''get data from redis database'''
        val = self._redis.get(key)  # Retrieving data from Redis
        if fn:
            val = fn(val)  # Applying conversion function if provided
        return val  # Returning the retrieved data

    def get_str(self, key: str) -> str:
        '''retrieves data from redis and converts them to utf-8'''
        val = self._redis.get(key)  # Retrieving data from Redis
        return val.decode("utf-8")  # Converting data to string and returning

    def get_int(self, key: str) -> int:
        '''retrieves data from redis and converts them to integer'''
        val = self._redis.get(key)  # Retrieving data from Redis
        try:
            val = int(val.decode("utf-8"))  # Converting data to integer
        except Exception:
            val = 0  # Handling conversion errors
        return val  # Returning the converted data
