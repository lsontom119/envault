"""Encryption and decryption utilities for envault using Fernet symmetric encryption."""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


SALT_SIZE = 16
ITERATIONS = 390_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(plaintext: str, password: str) -> bytes:
    """
    Encrypt plaintext with a password.
    Returns salt + encrypted data as raw bytes.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    token = Fernet(key).encrypt(plaintext.encode())
    return salt + token


def decrypt(data: bytes, password: str) -> str:
    """
    Decrypt data produced by `encrypt`.
    Raises ValueError on wrong password or corrupted data.
    """
    salt, token = data[:SALT_SIZE], data[SALT_SIZE:]
    key = derive_key(password, salt)
    try:
        return Fernet(key).decrypt(token).decode()
    except InvalidToken:
        raise ValueError("Decryption failed: invalid password or corrupted data.")
