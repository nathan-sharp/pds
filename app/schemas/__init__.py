"""Pydantic schemas package."""

from app.schemas.common import APIResponse
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.oauth import (
    OAuthAuthorizeRequest,
    OAuthTokenExchangeRequest,
    OAuthAuthorizeResponse,
)
from app.schemas.sync import (
    EncryptedRecordPayload,
    SyncPushRequest,
    SyncPullResponse,
)
from app.schemas.identity import (
    DIDDocument,
    RegisterKeysRequest,
    IdentityResponse,
)
from app.schemas.records import (
    PublicRecordCreateRequest,
    PublicRecordResponse,
    PublicRecordListResponse,
)

__all__ = [
    "APIResponse",
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserResponse",
    "OAuthAuthorizeRequest",
    "OAuthTokenExchangeRequest",
    "OAuthAuthorizeResponse",
    "EncryptedRecordPayload",
    "SyncPushRequest",
    "SyncPullResponse",
    "DIDDocument",
    "RegisterKeysRequest",
    "IdentityResponse",
    "PublicRecordCreateRequest",
    "PublicRecordResponse",
    "PublicRecordListResponse",
]
