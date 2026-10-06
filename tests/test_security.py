"""Unit tests for cryptographic security primitives (IEEE 29119)."""

import base64
import hashlib
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
    verify_pkce,
)


def test_argon2id_password_hashing():
    """Verify Argon2id password hash generation and verification."""
    # Arrange
    plain_pass = "Correct-Horse-Battery-Staple-2026!"
    wrong_pass = "Incorrect-Horse-Battery-Staple-2026!"

    # Act
    hashed = hash_password(plain_pass)
    valid_result = verify_password(plain_pass, hashed)
    invalid_result = verify_password(wrong_pass, hashed)

    # Assert
    assert valid_result is True
    assert invalid_result is False
    assert hashed.startswith("$argon2id$")


def test_pkce_s256_verification_success():
    """Verify valid PKCE code_verifier matches S256 code_challenge."""
    # Arrange
    verifier = "E9Melhoa2OwvFrGMTJguCH5rtG6jQu-hNMiqiUXQ57c"
    sha256_digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(sha256_digest).decode("ascii").rstrip("=")

    # Act
    is_valid = verify_pkce(code_verifier=verifier, code_challenge=challenge, method="S256")

    # Assert
    assert is_valid is True


def test_pkce_s256_verification_mismatch():
    """Verify mismatched PKCE code_verifier fails closed."""
    # Arrange
    verifier = "E9Melhoa2OwvFrGMTJguCH5rtG6jQu-hNMiqiUXQ57c"
    tampered_challenge = "InvalidChallengeStringForTestingMismatchVerification123"

    # Act
    is_valid = verify_pkce(code_verifier=verifier, code_challenge=tampered_challenge, method="S256")

    # Assert
    assert is_valid is False


def test_jwt_token_encode_and_decode_lifecycle():
    """Verify access token creation and payload decode integrity."""
    # Arrange
    user_id = "0192384f-7c15-7000-8d59-2b02874f63c8"
    client_id = "chirp"

    # Act
    token = create_access_token(subject=user_id, client_id=client_id)
    decoded = decode_access_token(token)

    # Assert
    assert decoded is not None
    assert decoded["sub"] == user_id
    assert decoded["aud"] == client_id
    assert decoded["iss"] == "pds-auth-hub"
    assert "exp" in decoded
