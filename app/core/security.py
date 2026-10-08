"""Cryptographic and Authentication Primitives."""

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

# Argon2id hasher configuration
# Parameters: memory_cost = 65536 KiB (64 MiB), time_cost = 3 iterations, parallelism = 4 lanes
hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hash password string using Argon2id."""
    return hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against Argon2id hash with side-effect free equality check."""
    try:
        return hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False


def generate_secure_token(entropy_bytes: int = 32) -> str:
    """Generate cryptographically secure URL-safe token. Minimum 256 bits of entropy."""
    return secrets.token_urlsafe(entropy_bytes)


def create_access_token(
    subject: str,
    client_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate signed JWT access token containing subject and optional client scope."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "iss": "pds-auth-hub",
    }
    if client_id:
        payload["aud"] = client_id

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT access token. Fail closed on error."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            issuer="pds-auth-hub",
            options={"require": ["exp", "iat", "sub"]},
        )
        return payload
    except (jwt.PyJWTError, Exception):
        return None


def verify_pkce(code_verifier: str, code_challenge: str, method: str = "S256") -> bool:
    """Verify Proof Key for Code Exchange (RFC 7636). Supports S256 transformation."""
    if method != "S256":
        return False

    # Compute SHA256 digest of ASCII code_verifier
    sha256_digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    # Compute base64url encoding without padding
    calculated_challenge = (
        base64.urlsafe_b64encode(sha256_digest).decode("ascii").rstrip("=")
    )

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(calculated_challenge, code_challenge.rstrip("="))


def canonicalize_json(data: Any) -> bytes:
    """Serialize object to deterministic, sorted, whitespace-free canonical JSON bytes."""
    import json

    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def verify_ed25519_signature(
    public_key_b64: str, data: bytes, signature_b64: str
) -> bool:
    """Verify Ed25519 digital signature over raw bytes. Fail closed on format error."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    try:
        # Standard or URL-safe base64 decoding with padding tolerance
        pad_key = public_key_b64 + "=" * (-len(public_key_b64) % 4)
        key_bytes = base64.urlsafe_b64decode(pad_key)

        pad_sig = signature_b64 + "=" * (-len(signature_b64) % 4)
        sig_bytes = base64.urlsafe_b64decode(pad_sig)

        pubkey = Ed25519PublicKey.from_public_bytes(key_bytes)
        pubkey.verify(sig_bytes, data)
        return True
    except (InvalidSignature, ValueError, Exception):
        return False
