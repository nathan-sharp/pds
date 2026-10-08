"""W3C Decentralized Identifier (DID) Document Generator Service."""

from typing import Any, Dict
from app.core.config import settings
from app.models.user import User


def build_server_did_document() -> Dict[str, Any]:
    """Generate W3C DID Core 1.0 document for the ARC PDS root node."""
    server_did = f"did:web:{settings.SERVER_DOMAIN}"
    return {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/suites/ed25519-2020/v1",
        ],
        "id": server_did,
        "service": [
            {
                "id": f"{server_did}#pds-service",
                "type": "ArcPersonalDataServer",
                "serviceEndpoint": f"https://{settings.SERVER_DOMAIN}{settings.API_V1_STR}",
            }
        ],
    }


def build_user_did_document(user: User) -> Dict[str, Any]:
    """Generate W3C DID Core 1.0 document for an individual PDS user identity."""
    verification_methods = []
    authentication = []
    assertion_methods = []
    key_agreements = []

    if user.signing_key_ed25519:
        key_id = f"{user.did}#key-1"
        verification_methods.append(
            {
                "id": key_id,
                "type": "Ed25519VerificationKey2020",
                "controller": user.did,
                "publicKeyBase64": user.signing_key_ed25519,
            }
        )
        authentication.append(key_id)
        assertion_methods.append(key_id)

    if user.encryption_key_x25519:
        enc_key_id = f"{user.did}#key-enc-1"
        verification_methods.append(
            {
                "id": enc_key_id,
                "type": "X25519KeyAgreementKey2020",
                "controller": user.did,
                "publicKeyBase64": user.encryption_key_x25519,
            }
        )
        key_agreements.append(enc_key_id)

    doc: Dict[str, Any] = {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/suites/ed25519-2020/v1",
            "https://w3id.org/security/suites/x25519-2020/v1",
        ],
        "id": user.did,
        "alsoKnownAs": [f"arc://{user.pds_id}@{settings.SERVER_DOMAIN}"],
        "verificationMethod": verification_methods,
        "authentication": authentication,
        "assertionMethod": assertion_methods,
        "keyAgreement": key_agreements,
        "service": [
            {
                "id": f"{user.did}#pds",
                "type": "PersonalDataServer",
                "serviceEndpoint": f"https://{settings.SERVER_DOMAIN}{settings.API_V1_STR}",
            }
        ],
    }
    return doc
