import pytest
from app.main import app
from app.api.deps import get_current_user
from app.models.user import User
from app.models.webhook import WebhookSubscription
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

client = TestClient(app)

# Mock user for dependencies
mock_user = User(
    id=str(uuid.uuid4()),
    pds_id="testuser",
    did="did:web:example.com:users:testuser",
    hashed_password="mock_hash",
)

@pytest.fixture
def mock_db_session():
    session = AsyncMock(spec=AsyncSession)
    return session

@pytest.fixture(autouse=True)
def override_dependencies(mock_db_session):
    from app.db.session import get_db

    async def _override_get_db():
        yield mock_db_session

    async def _override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


from datetime import datetime, timezone
from unittest.mock import MagicMock

def test_create_webhook(mock_db_session: AsyncSession):
    async def mock_refresh(instance):
        instance.id = "test-webhook-id"
        instance.created_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db_session.commit = AsyncMock()
    mock_db_session.add = MagicMock()

    payload = {
        "target_url": "https://example.com/webhook",
        "events": ["record.created", "record.updated"],
    }

    response = client.post("/api/v1/webhooks/subscriptions/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["target_url"] == payload["target_url"]
    assert data["events"] == payload["events"]
    assert "secret" in data
    assert "id" in data
    assert data["is_active"] is True


def test_list_webhooks(mock_db_session: AsyncSession):
    webhook = WebhookSubscription(
        id="test-webhook-id",
        user_id=mock_user.id,
        target_url="https://example.com/webhook2",
        events=["record.deleted"],
        secret="testsecret",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Mock the database result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [webhook]
    mock_db_session.execute.return_value = mock_result
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()
    mock_db_session.add = MagicMock()

    response = client.get("/api/v1/webhooks/subscriptions/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["target_url"] == "https://example.com/webhook2"


def test_delete_webhook(mock_db_session: AsyncSession):
    webhook_id = "test-webhook-id"
    webhook = WebhookSubscription(
        id=webhook_id,
        user_id=mock_user.id,
        target_url="https://example.com/webhook3",
        events=["record.created"],
        secret="testsecret2",
        is_active=True,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = webhook
    mock_db_session.execute.return_value = mock_result
    mock_db_session.commit = AsyncMock()

    response = client.delete(f"/api/v1/webhooks/subscriptions/{webhook_id}")
    assert response.status_code == 204

    # Check that it was marked inactive
    assert webhook.is_active is False
    mock_db_session.commit.assert_awaited()
