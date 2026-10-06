"""Authentication and User Pydantic Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserRegisterRequest(BaseModel):
    """Payload to register a new PDS ID."""

    model_config = ConfigDict(extra="forbid")

    pds_id: str = Field(
        ...,
        min_length=3,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_\-\.]+$",
        description="Unique PDS identifier (alphanumeric, dots, underscores, dashes)",
    )
    password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="Master passphrase (minimum 12 characters)",
    )
    public_identity_key: Optional[str] = Field(
        default=None,
        description="Client-side generated public identity key (e.g. Ed25519/X25519)",
    )
    encrypted_key_envelope: Optional[str] = Field(
        default=None,
        description="Client-encrypted master key envelope for cross-device sync",
    )


class UserLoginRequest(BaseModel):
    """Direct PDS ID authentication payload."""

    model_config = ConfigDict(extra="forbid")

    pds_id: str = Field(..., description="PDS identifier")
    password: str = Field(..., description="Master passphrase")


class TokenResponse(BaseModel):
    """OAuth2 / JWT token response envelope."""

    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str = ""


class UserResponse(BaseModel):
    """User profile response."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str
    pds_id: str
    public_identity_key: Optional[str] = None
    encrypted_key_envelope: Optional[str] = None
    created_at: datetime
