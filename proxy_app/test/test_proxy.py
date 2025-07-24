from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from jose import jwt, ExpiredSignatureError
from unittest.mock import AsyncMock

from auth import create_access_token
from config import ALGORITHM, KEY
from proxy_app.main import app

@patch("proxy_app.auth.datetime.datetime")
def test_token_success(mock_auth):
    fixed_now = datetime(2025, 1 ,1, 12, 0, 0, tzinfo=timezone.utc)
    mock_auth.now.return_value = fixed_now
    mock_auth.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    data = {"sub": "test_user" }
    expires_delta = timedelta(minutes=10)

    token = create_access_token(data, expires_delta=expires_delta)

    decoded = jwt.decode(token, KEY, algorithms=[ALGORITHM], options={"verify_exp": False})

    expected_exp = int((fixed_now + expires_delta).timestamp())
    actual_exp = decoded["exp"]

    print(f"Expected: {expected_exp}, Actual: {actual_exp}")

    assert actual_exp == expected_exp
    assert isinstance(token, str)
    parts = token.split(".")
    assert len(parts) == 3
    assert token



@patch("proxy_app.auth.datetime.datetime")
def test_token_expired_raises_error(mock_auth):
    fixed_now = datetime(2025, 1 ,1, 12, 0, 0, tzinfo=timezone.utc)
    mock_auth.now.return_value = fixed_now
    mock_auth.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    expires_delta = timedelta(minutes=-5)
    data = {"sub": "expired_user"}

    token = create_access_token(data, expires_delta=expires_delta)

    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token, KEY, algorithms=[ALGORITHM])

client = TestClient(app)

@patch("proxy_app.main.user_exists_in_db", new_callable=AsyncMock, return_value=True)
def test_login_success(mock_user_exists):
    username = "test_user"
    password = "test_password"

    response = client.post("/token", data={"username": username, "password": password})

    assert response.status_code == 200

    tokens = response.json()

    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    for token_name in ("access_token", "refresh_token"):
        token = tokens[token_name]
        assert isinstance(token, str)
        assert len(token.split(".")) == 3

        decoded = jwt.decode(token, KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        assert decoded["sub"] == username

@patch("proxy_app.main.user_exists_in_db", new_callable=AsyncMock, return_value=False)
def test_login_invalid_credentials(mock_user_exists):
    response = client.post("/token", data={"username": "bad_user", "password": "wrong_pass"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


























