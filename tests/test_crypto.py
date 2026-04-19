"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DB_URL=postgres://user:pass@localhost/mydb\nAPI_KEY=abc123"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_decrypt_roundtrip():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(ciphertext, PASSWORD)
    assert recovered == PLAINTEXT


def test_different_encryptions_produce_different_output():
    """Each encryption should use a fresh random salt."""
    c1 = encrypt(PLAINTEXT, PASSWORD)
    c2 = encrypt(PLAINTEXT, PASSWORD)
    assert c1 != c2


def test_decrypt_wrong_password_raises():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="invalid password or corrupted data"):
        decrypt(ciphertext, "wrong-password")


def test_decrypt_corrupted_data_raises():
    ciphertext = bytearray(encrypt(PLAINTEXT, PASSWORD))
    ciphertext[20] ^= 0xFF  # flip bits in the token portion
    with pytest.raises(ValueError):
        decrypt(bytes(ciphertext), PASSWORD)


def test_empty_plaintext_roundtrip():
    ciphertext = encrypt("", PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == ""
