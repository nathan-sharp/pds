"""Common Pydantic Schemas."""

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized API response container."""

    model_config = ConfigDict(extra="forbid")

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
