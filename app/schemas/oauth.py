"""OAuth 2.0 and PKCE Schemas for PDS SSO Hub."""

from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class OAuthAuthorizeRequest(BaseModel):
    """Payload to authorize an application and issue a code (RFC 7636)."""

    model_config = ConfigDict(extra="forbid")

    client_id: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="Target client application identifier (e.g., chirp, burrow)",
    )
    response_type: Literal["code"] = Field(
        "code", description="OAuth2 response type, must be 'code'"
    )
    redirect_uri: str = Field(..., description="Callback URL for client application")
    code_challenge: str = Field(
        ...,
        min_length=43,
        max_length=128,
        description="PKCE code challenge (SHA256 digest in base64url)",
    )
    code_challenge_method: Literal["S256"] = Field(
        "S256", description="PKCE transformation method. Enforces S256."
    )
    scope: str = Field(default="openid sync", description="Requested permission scope")
    state: Optional[str] = Field(
        default=None, description="Anti-CSRF state token passed by client"
    )

    # User credential payload for the login screen within the PDS SSO flow
    pds_id: str = Field(..., description="User PDS ID")
    password: str = Field(..., description="User Master Passphrase")


class OAuthTokenExchangeRequest(BaseModel):
    """Payload for token endpoint code exchange or token refresh."""

    model_config = ConfigDict(extra="forbid")

    grant_type: Literal["authorization_code", "refresh_token"] = Field(
        ..., description="Grant type: 'authorization_code' or 'refresh_token'"
    )
    client_id: str = Field(..., description="Registered client application identifier")
    code: Optional[str] = Field(
        default=None, description="Authorization code from authorize endpoint"
    )
    code_verifier: Optional[str] = Field(
        default=None,
        min_length=43,
        max_length=128,
        description="PKCE original random verifier string",
    )
    redirect_uri: Optional[str] = Field(
        default=None, description="Redirect URI matching authorization request"
    )
    refresh_token: Optional[str] = Field(
        default=None, description="Refresh token for token renewal"
    )


class OAuthAuthorizeResponse(BaseModel):
    """Response containing authorization code for redirection."""

    model_config = ConfigDict(extra="forbid")

    code: str
    state: Optional[str] = None
    redirect_uri: str
