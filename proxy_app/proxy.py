import httpx
import json
import logging

from fastapi import Request, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from proxy_app.cache import make_cache_key
from proxy_app.logger import log_request_info, log_response_info
from proxy_app.config import FASTAPI_TARGET

logger = logging.getLogger("proxy_logger")

@cache(expire=30)
async def cached_get_request(method: str, url: str, headers: dict):
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, headers=headers)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text,
        }

async def forward_request(request: Request, path: str):
    method = request.method
    url = f"{FASTAPI_TARGET}{path}"
    if request.query_params:
        url += f"?{request.query_params}"

    headers = dict(request.headers)
    query_params = str(request.query_params)
    body = await request.body()

    log_request_info({
        "method": method,
        "url": url,
        "headers": headers,
        "body": body.decode(errors="ignore")
    })

    cache_key = make_cache_key(method, url, body, query_params)
    cache_backend: RedisBackend = FastAPICache.get_backend()

    if method in ["GET", "POST"]:
        cached_raw = await cache_backend.get(cache_key)
        if cached_raw:
            try:
                cached = json.loads(cached_raw)
                logger.info(">>> Ответ из КЭША Redis!")
                return httpx.Response(
                    status_code=cached["status_code"],
                    content=cached["content"],
                    headers=cached["headers"]
                )
            except Exception as e:
                logger.warning(f"Ошибка при разборе кеша: {e}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, headers=headers, content=body)
                log_response_info({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text
                })


                await cache_backend.set(cache_key, json.dumps({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.text
                }), expire=30)

                return response
            except httpx.RequestError as e:
                raise HTTPException(status_code=502, detail=str(e))
    else:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, headers=headers, content=body)
                log_response_info({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text
                })
                return response
            except httpx.RequestError as e:
                raise HTTPException(status_code=502, detail=str(e))
