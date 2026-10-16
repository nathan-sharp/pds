"""Webhook Subscription Endpoints."""

import secrets
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.webhook import WebhookSubscription
from app.schemas.webhook import WebhookCreate, WebhookResponse, WebhookResponseWithSecret

router = APIRouter()


@router.post(
    "/",
    response_model=WebhookResponseWithSecret,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new webhook subscription",
)
async def create_webhook(
    request: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new webhook subscription for real-time event delivery."""
    secret = request.secret or secrets.token_urlsafe(32)

    new_webhook = WebhookSubscription(
        user_id=current_user.id,
        target_url=str(request.target_url),
        events=request.events,
        secret=secret,
        is_active=True,
    )

    db.add(new_webhook)
    await db.commit()
    await db.refresh(new_webhook)

    return new_webhook


@router.get(
    "/",
    response_model=List[WebhookResponse],
    summary="List active webhook subscriptions",
)
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all webhook subscriptions for the authenticated user."""
    stmt = select(WebhookSubscription).where(
        WebhookSubscription.user_id == current_user.id,
        WebhookSubscription.is_active.is_(True),
    )
    result = await db.execute(stmt)
    webhooks = result.scalars().all()

    return webhooks


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a webhook subscription",
)
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete (deactivate) a webhook subscription."""
    stmt = select(WebhookSubscription).where(
        WebhookSubscription.id == webhook_id,
        WebhookSubscription.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found",
        )

    # We softly delete by marking it inactive, or we can hard delete
    # Given the roadmap description, let's hard delete to clean up DB, or soft delete if preferred.
    # To keep the sync blob and public record patterns, let's just delete it from the database for simplicity,
    # or follow the is_active flag convention.
    webhook.is_active = False
    await db.commit()

    return None
