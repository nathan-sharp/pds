"""W3C Decentralized Identifier (DID) and Cryptographic Key Schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DIDDocument(BaseModel):
    """W3C DID Core 1.0 compliant document."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: List[str] = Field(
        default=[
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/suites/ed25519-2020/v1",
            "https://w3id.org/security/suites/x25519-2020/v1",
        ],
        alias="@context",
    )
    id: str = Field(..., description="Target Decentralized Identifier")
    alsoKnownAs: Optional[List[str]] = Field(default=None)
    verificationMethod: List[Dict[str, Any]] = Field(default_factory=list)
    authentication: List[str] = Field(default_factory=list)
    assertionMethod: List[str] = Field(default_factory=list)
    keyAgreement: List[str] = Field(default_factory=list)
    service: List[Dict[str, Any]] = Field(default_factory=list)


class RegisterKeysRequest(BaseModel):
    """Payload to register or rotate cryptographic identity keys."""

    model_config = ConfigDict(extra="forbid")

    signing_key_ed25519: str = Field(
        ...,
        min_length=32,
        max_length=128,
        description="Base64-encoded Ed25519 public key (32 raw bytes)",
    )
    encryption_key_x25519: Optional[str] = Field(
        default=None,
        min_length=32,
        max_length=128,
        description="Base64-encoded Curve25519 (X25519) public key (32 raw bytes)",
    )
    encrypted_key_envelope: Optional[str] = Field(
        default=None,
        description="Client-encrypted private key envelope for cross-device synchronization",
    )


class IdentityResponse(BaseModel):
    """Summary of registered identity and public keys."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    pds_id: str
    did: str
    signing_key_ed25519: Optional[str] = None
    encryption_key_x25519: Optional[str] = None
