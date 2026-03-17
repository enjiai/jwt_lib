"""Payload decryption utilities for JWT tokens."""

import base64
import json
import zlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_NONCE_SIZE = 12


def _derive_key(secret: str) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"enji-jwt-payload-encryption",
    ).derive(secret.encode())


def decrypt_payload(token: str, secret: str) -> dict:
    """Decrypt and decompress a base64url string back to a dict of JWT claims."""
    raw = base64.urlsafe_b64decode(token)
    nonce, ciphertext = raw[:_NONCE_SIZE], raw[_NONCE_SIZE:]
    plaintext = AESGCM(_derive_key(secret)).decrypt(nonce, ciphertext, None)
    return json.loads(zlib.decompress(plaintext))
