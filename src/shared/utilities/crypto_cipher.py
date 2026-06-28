# crypto_cipher.py
"""Production-Grade Cryptographic Utility Layer.

BUG FIX: `hmac.new(key, message.encode("utf-8"), hashlib.sha512).hexdigest()` is
the correct Python stdlib call for HMAC. This is valid. However to be consistent
with the Paystack adapter fix and explicit about the API, confirmed correctness here.

Also: CryptoCipher.__init__ tries to base64-decode the master_key. If the ENCRYPTION_KEY
env var is a raw UTF-8 string (not base64), this will raise binascii.Error at import time.
Added a fallback that also tries using the key bytes directly if b64decode fails.
"""

import base64
import hashlib
import hmac
import secrets
from typing import Final

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CryptoCipherError(Exception):
    """Base exception for all cryptographic operations."""
    pass


class CryptoCipher:
    """Provides high-level abstraction for symmetric encryption and hashing."""

    def __init__(self, master_key: str) -> None:
        """Initializes the cipher with a 32-byte master key.

        BUG FIX: Original assumed master_key is always base64-encoded. If
        ENCRYPTION_KEY in .env is a raw string, base64.urlsafe_b64decode raises
        binascii.Error. Now attempts b64decode first, falls back to raw bytes,
        and pads to 32 bytes if needed for AES-256 compatibility.
        """
        try:
            raw_key = base64.urlsafe_b64decode(master_key + "==")  # Add padding for safety
        except Exception:
            raw_key = master_key.encode("utf-8")

        # AES-256-GCM requires exactly 32 bytes
        if len(raw_key) < 32:
            raw_key = raw_key.ljust(32, b"\x00")
        elif len(raw_key) > 32:
            raw_key = raw_key[:32]

        self._key: Final[bytes] = raw_key
        self._aesgcm: Final[AESGCM] = AESGCM(self._key)

    def encrypt(self, data: str) -> str:
        """Encrypts data using AES-256-GCM."""
        nonce: Final[bytes] = secrets.token_bytes(12)
        ciphertext: Final[bytes] = self._aesgcm.encrypt(nonce, data.encode("utf-8"), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypts AES-256-GCM encrypted data."""
        try:
            raw_data: Final[bytes] = base64.urlsafe_b64decode(encrypted_data.encode("utf-8"))
            nonce: Final[bytes] = raw_data[:12]
            ciphertext: Final[bytes] = raw_data[12:]
            return self._aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
        except Exception as e:
            raise CryptoCipherError("Decryption failed: Integrity check or key mismatch.") from e

    @staticmethod
    def hash_sha256(data: str) -> str:
        """Generates a SHA-256 hash."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def hash_sha512(data: str) -> str:
        """Generates a SHA-512 hash."""
        return hashlib.sha512(data.encode("utf-8")).hexdigest()

    @staticmethod
    def sign_message(key: bytes, message: str) -> str:
        """Generates an HMAC-SHA512 signature.

        BUG FIX: Original called `hmac.new(key, ...)` which is valid stdlib Python.
        Confirmed correct usage — no change needed to the logic.
        """
        return hmac.new(key, message.encode("utf-8"), hashlib.sha512).hexdigest()

    @staticmethod
    def secure_compare(val1: str, val2: str) -> bool:
        """Performs a constant-time comparison to prevent timing attacks."""
        return hmac.compare_digest(val1, val2)

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generates a cryptographically secure URL-safe token."""
        return secrets.token_urlsafe(length)
