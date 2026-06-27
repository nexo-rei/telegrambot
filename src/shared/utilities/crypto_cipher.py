# crypto_cipher.py
"""Production-Grade Cryptographic Utility Layer.

Provides a centralized, secure interface for performing data encryption, hashing, 
and message signing. Utilizes industry-standard primitives such as AES-256-GCM 
and HMAC-SHA512 to protect sensitive financial and personal identifiable information 
(PII) within the platform, ensuring compliance with enterprise security mandates.
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
        """Initializes the cipher with a 32-byte master key."""
        self._key: Final[bytes] = base64.urlsafe_b64decode(master_key)
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
        """Generates an HMAC-SHA512 signature."""
        return hmac.new(key, message.encode("utf-8"), hashlib.sha512).hexdigest()

    @staticmethod
    def secure_compare(val1: str, val2: str) -> bool:
        """Performs a constant-time comparison to prevent timing attacks."""
        return hmac.compare_digest(val1, val2)

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generates a cryptographically secure URL-safe token."""
        return secrets.token_urlsafe(length)
