"""
Runtime configuration loaded from environment variables.

Secrets intentionally do not have source-code defaults. For local
development, create a .env file from .env.example.
"""

import base64
import binascii
import os

from dotenv import load_dotenv


load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_jwt_secret() -> str:
    return require_env("JWT_SECRET_KEY")


def get_aes_key() -> bytes:
    raw = require_env("AES_KEY")
    try:
        key = base64.b64decode(raw, validate=True)
    except binascii.Error as exc:
        raise RuntimeError("AES_KEY must be base64-encoded 32 random bytes") from exc

    if len(key) != 32:
        raise RuntimeError("AES_KEY must decode to exactly 32 bytes for AES-256")
    return key
