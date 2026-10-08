"""Unit tests for W3C Decentralized Identity (DID) and Ed25519 signature primitives (IEEE 29119)."""

import base64
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.core.security import canonicalize_json, verify_ed25519_signature
from app.models.user import User
from app.services.identity_service import build_server_did_document, build_user_did_document


def test_ed25519_signature_verification_success():
    """Verify valid Ed25519 digital signature over canonicalized JSON data."""
    # Arrange
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    pub_bytes = public_key.public_bytes_raw()
    pub_b64 = base64.urlsafe_b64encode(pub_bytes).decode("ascii")

    payload = {"author": "alice", "text": "Hello decentralized world!", "timestamp": 1728412800}
    canonical_bytes = canonicalize_json(payload)
    sig_bytes = private_key.sign(canonical_bytes)
    sig_b64 = base64.urlsafe_b64encode(sig_bytes).decode("ascii")

    # Act
    is_valid = verify_ed25519_signature(pub_b64, canonical_bytes, sig_b64)

    # Assert
    assert is_valid is True


def test_ed25519_signature_verification_tampered_payload_failure():
    """Verify tampered payload fails closed during Ed25519 verification."""
    # Arrange
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    pub_bytes = public_key.public_bytes_raw()
    pub_b64 = base64.urlsafe_b64encode(pub_bytes).decode("ascii")

    original_payload = {"author": "alice", "text": "Original message"}
    tampered_payload = {"author": "alice", "text": "Tampered message"}

    canonical_orig = canonicalize_json(original_payload)
    canonical_tampered = canonicalize_json(tampered_payload)

    sig_bytes = private_key.sign(canonical_orig)
    sig_b64 = base64.urlsafe_b64encode(sig_bytes).decode("ascii")

    # Act
    is_valid = verify_ed25519_signature(pub_b64, canonical_tampered, sig_b64)

    # Assert
    assert is_valid is False


def test_w3c_server_did_document_structure():
    """Verify root server DID document adheres to W3C did:web standard."""
    # Arrange / Act
    doc = build_server_did_document()

    # Assert
    assert "@context" in doc
    assert "id" in doc
    assert doc["id"].startswith("did:web:")
    assert len(doc["service"]) >= 1


def test_w3c_user_did_document_structure():
    """Verify user DID document includes Ed25519 verificationMethod and assertionMethod."""
    # Arrange
    user = User(
        id="test-uuid-1",
        pds_id="bob",
        did="did:web:localhost:8000:users:bob",
        hashed_password="mock-hash",
        signing_key_ed25519="MC4CAQAwBQYDK2VwBCIEIPn...mock...",
        encryption_key_x25519="MC4CAQAwBQYDK2VuBCIEIKg...mock...",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    # Act
    doc = build_user_did_document(user)

    # Assert
    assert doc["id"] == "did:web:localhost:8000:users:bob"
    assert len(doc["verificationMethod"]) == 2
    assert f"{user.did}#key-1" in doc["authentication"]
    assert f"{user.did}#key-1" in doc["assertionMethod"]
    assert f"{user.did}#key-enc-1" in doc["keyAgreement"]
