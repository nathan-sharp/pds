"""Public Federated Records Schemas (Zone 2)."""

from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class PublicRecordCreateRequest(BaseModel):
    """Payload to create or update a signed public federated record."""

    model_config = ConfigDict(extra="forbid")

    collection: str = Field(
        ...,
        min_length=1,
        max_length=128,
        pattern=r"^[a-zA-Z0-9_\-\.]+$",
        description="Logical collection name (e.g., flock.post, social.profile)",
    )
    record_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Unique record identifier authored by the client",
    )
    content: Dict[str, Any] = Field(
        ..., description="Arbitrary public JSON document payload"
    )
    signature: str = Field(
        ...,
        min_length=32,
        max_length=256,
        description="Base64-encoded Ed25519 digital signature over canonicalized content JSON",
    )


class PublicRecordResponse(BaseModel):
    """Public federated record output model."""

    model_config = ConfigDict(extra="forbid")

    id: str
    did: str
    collection: str
    record_id: str
    content: Dict[str, Any]
    signature: str
    created_at: datetime
    updated_at: datetime


class PublicRecordListResponse(BaseModel):
    """Paginated collection of public records."""

    model_config = ConfigDict(extra="forbid")

    records: List[PublicRecordResponse]
    total: int
