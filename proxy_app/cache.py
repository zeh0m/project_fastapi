import hashlib

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis

def make_cache_key(method: str, url: str, body: bytes, query_params: str) -> str:
    body_hash = hashlib.md5(body).hexdigest() if body else "no_body"
    return f"{method}:{url}?{query_params}:body_hash={body_hash}"