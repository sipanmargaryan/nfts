import random
import re
import secrets
import string
import time
from datetime import datetime, timedelta, timezone

from passlib.hash import bcrypt

from app.helpers.jwt import create_access_token, create_refresh_token
from app.routers.auth.models import Account


def get_password_hash(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)


def generate_auth_code() -> str:
    random_string = secrets.token_urlsafe(16)
    timestamp = int(time.time())

    return f"{random_string}-{timestamp}"


def generate_reset_code() -> str:
    return "".join(random.choices(string.digits, k=6))


def get_timedelta_from_hours(**kwargs) -> datetime:
    return datetime.now(timezone.utc) + timedelta(**kwargs)


def get_token_payload(data) -> dict:
    return {
        "email": data.email,
        "first_name": data.user_profile.first_name,
        "last_name": data.user_profile.last_name,
        "user_id": data.id,
    }


def generate_tokens(data: Account, refresh: str = "") -> dict:
    tokens = dict(refresh_token=refresh)
    token_payload = get_token_payload(data)
    tokens["access_token"] = create_access_token(token_payload)
    if not refresh:
        tokens["refresh_token"] = create_refresh_token(token_payload)
    return tokens
