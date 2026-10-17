import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.webhook import WebhookSubscription
from app.schemas.webhook import WebhookSubscriptionCreate, WebhookSubscriptionResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/subscriptions",
    response_model=WebhookSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a Webhook Subscription",
    description="Registers a new webhook URL to receive streaming events."
)
async def create_webhook_subscription(
    subscription_in: WebhookSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new webhook subscription for the authenticated user."""
    subscription = WebhookSubscription(
        user_id=current_user.id,
        url=str(subscription_in.url),
        events=subscription_in.events,
        secret=subscription_in.secret,
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    return subscription


@router.get(
    "/subscriptions",
    response_model=List[WebhookSubscriptionResponse],
    summary="List Webhook Subscriptions",
    description="Retrieves a list of all active and inactive webhook subscriptions for the current user."
)
async def list_webhook_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists webhook subscriptions for the authenticated user."""
    stmt = select(WebhookSubscription).where(WebhookSubscription.user_id == current_user.id)
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()
    return subscriptions
