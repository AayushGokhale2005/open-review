"""Secure local token storage helpers."""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet

from openreview.core.config import Settings


def _derive_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_token(token: str, settings: Settings) -> str:
    fernet = Fernet(_derive_key(settings.token_encryption_key))
    return fernet.encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(token: str, settings: Settings) -> str:
    fernet = Fernet(_derive_key(settings.token_encryption_key))
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")
