import datetime
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import asyncpg

from proxy_app.config import KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from proxy_app.config import USER, PASSWORD, NAME, HOST, PORT

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, KEY, algorithm=ALGORITHM)

async def user_exists_in_db(username: str) -> bool:
    conn = await asyncpg.connect(
        user=USER,
        password=PASSWORD,
        database=NAME,
        host=HOST,
        port=PORT,
    )
    row = await conn.fetchrow("SELECT id FROM auth_user WHERE username = $1", username)
    await conn.close()
    return row is not None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username or not await user_exists_in_db(username):
            raise HTTPException(status_code=401, detail="Invalid token or user not found")
        return {"USER": username}
    except JWTError:
        raise HTTPException(status_code=403, detail="Token error")























