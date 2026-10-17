from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

class WebhookSubscriptionCreate(BaseModel):
    """Schema for creating a new webhook subscription."""
    url: HttpUrl = Field(..., description="The HTTPS URL where webhook events will be sent.")
    events: List[str] = Field(..., description="List of event types to subscribe to (e.g., ['record.created', 'record.updated']).")
    secret: Optional[str] = Field(None, description="Optional secret used to generate HMAC-SHA256 signatures for payload verification.")

class WebhookSubscriptionResponse(BaseModel):
    """Schema for a webhook subscription response."""
    id: str = Field(..., description="The unique identifier of the webhook subscription.")
    user_id: str = Field(..., description="The user ID who owns the subscription.")
    url: str = Field(..., description="The target URL.")
    events: List[str] = Field(..., description="List of subscribed event types.")
    is_active: bool = Field(..., description="Whether the subscription is currently active.")
    failure_count: int = Field(..., description="Number of consecutive delivery failures.")
    created_at: datetime = Field(..., description="When the subscription was created.")
    updated_at: datetime = Field(..., description="When the subscription was last updated.")

    model_config = {
        "from_attributes": True
    }
