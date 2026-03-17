"""Payload decryption utilities for JWT tokens."""

import base64
import json

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def _derive_fernet_key(secret: str) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"enji-jwt-payload-encryption",
    )
    return base64.urlsafe_b64encode(hkdf.derive(secret.encode()))


def decrypt_payload(token: str, secret: str) -> dict:
    """Decrypt an encrypted JWT claims string back to a dict."""
    plaintext = Fernet(_derive_fernet_key(secret)).decrypt(token.encode())
    return json.loads(plaintext)
