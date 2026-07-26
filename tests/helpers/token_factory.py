"""Test-only helpers mirroring enji-auth encrypt + HS256 minting."""

from __future__ import annotations

import base64
import json
import os
import zlib
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_NONCE_SIZE = 12


def derive_key(secret: str) -> bytes:
    """Derive encryption key using HKDF-SHA256 matching enji-auth pipeline."""
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"enji-jwt-payload-encryption",
    ).derive(secret.encode())


def encrypt_payload(data: dict[str, Any], secret: str) -> str:
    """Encrypt sensitive payload using AES-GCM + zlib, matching enji-auth."""
    nonce = os.urandom(_NONCE_SIZE)
    plaintext = zlib.compress(
        json.dumps(data, separators=(",", ":")).encode(),
        level=zlib.Z_BEST_COMPRESSION,
    )
    ciphertext = AESGCM(derive_key(secret)).encrypt(nonce, plaintext, None)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def make_access_token(
    secret: str,
    *,
    sub: str = "user@example.com",
    user_id: int = 1,
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
    disallows: list[str] | None = None,
    employee_id: int | None = 42,
    exp_delta: timedelta = timedelta(hours=1),
    algorithm: str = "HS256",
    extra_sensitive: dict[str, Any] | None = None,
    include_enc: bool = True,
) -> str:
    """Mint a JWT access token with encrypted sensitive claims."""
    exp_ts = int((datetime.now(UTC) + exp_delta).timestamp())
    sensitive: dict[str, Any] = {
        "sub": sub,
        "user_id": user_id,
        "rand_str": "test-rand-str",
        "roles": roles or [],
        "permissions": permissions or [],
        "disallows": disallows or [],
        "employee_id": employee_id,
    }
    if extra_sensitive:
        sensitive.update(extra_sensitive)
    public: dict[str, Any] = {"exp": exp_ts, "type": "access"}
    if include_enc:
        public["enc"] = encrypt_payload(sensitive, secret)
    else:
        public.update(sensitive)
    return str(jwt.encode(public, secret, algorithm=algorithm))
