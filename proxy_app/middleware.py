import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from getmac import get_mac_address
import aiohttp

from proxy_app.logger import log_request_info

async def get_geo(ip: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"http://ip.com/json{ip}?fields=country, city, regionName"
            ) as resp:
                return await resp.json()
    except:
        return {}

async def get_mac(ip: str) -> str:
    try:
        mac = get_mac_address(ip=ip)
        return mac or "unknown"
    except:
        return "unknown"

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        client_ip = request.client.host
        user_agent = request.headers.get("User-Agent", "unknown")
        method = request.method
        path = request.url.path
        body = await request.body()

        geo = await get_geo(ip=client_ip)
        mac = await get_mac(ip=client_ip)

        user = "anonymous"
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from config import KEY, ALGORITHM
            from jose import jwt
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
                user = payload.get("sub", "unknown")
            except:
                pass

        response = await call_next(request)

        duration = round((time.time() - start_time) * 1000, 2)

        log_request_info({
            "user": user,
            "client_ip": client_ip,
            "mac": mac,
            "geo": geo,
            "method": method,
            "path": path,
            "user_agent": user_agent,
            "duration_ms": duration,
            "status_code": response.status_code,
            "body": body.decode(errors="ignore"),
        })

        return response















