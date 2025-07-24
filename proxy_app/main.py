from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi import FastAPI, Request, Response, Depends, Form, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from proxy_app.middleware import RequestLoggingMiddleware
from proxy_app.proxy import forward_request
from proxy_app.auth import create_access_token, create_refresh_token, get_current_user, user_exists_in_db
from proxy_app.config import ALGORITHM, PASSWORD


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url("redis://redis:6379", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

    yield

    print("Shutdown, clean up here if needed")
    await redis_client.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)

@app.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    user_ok = await user_exists_in_db(username)
    if not user_ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": username})
    refresh_token = create_refresh_token({"sub": username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@app.post("/refresh")
async def refresh_token(refresh_token: str = Form(...)):
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(refresh_token, PASSWORD, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        if not username:
            raise ValueError()
        new_token = create_access_token({"sub": username})
        return {"access_token": new_token}
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

@app.api_route("/proxy/{full_path:path}", methods=["GET", "POST", "PATCH", "DELETE", "PUT"])
async def proxy(full_path: str, request: Request, user=Depends(get_current_user)):
    response = await forward_request(request, full_path)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )















