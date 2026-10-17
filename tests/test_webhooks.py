import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.webhook import WebhookSubscription

client = TestClient(app)

@pytest.fixture
def mock_current_user():
    user = MagicMock()
    user.id = "user-123"
    return user

def test_create_webhook_subscription(mock_current_user):
    payload = {
        "url": "https://example.com/webhook",
        "events": ["record.created"],
        "secret": "my-secret-token"
    }

    with patch("app.api.v1.endpoints.webhooks.get_current_user", return_value=mock_current_user), \
         patch("app.api.v1.endpoints.webhooks.get_db") as mock_get_db:

        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Override the dependency for the test client
        from app.api.deps import get_current_user, get_db
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        app.dependency_overrides[get_db] = lambda: mock_db

        # We need a side effect for refresh to populate the id
        async def mock_refresh(instance):
            instance.id = "sub-123"
            import datetime
            dt = datetime.datetime.now(datetime.timezone.utc)
            instance.created_at = dt
            instance.updated_at = dt
            instance.is_active = True
            instance.failure_count = 0

        mock_db.refresh.side_effect = mock_refresh

        response = client.post("/api/v1/webhooks/subscriptions", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://example.com/webhook"
        assert data["events"] == ["record.created"]
        assert data["user_id"] == "user-123"
        assert data["is_active"] is True

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # Clean up overrides
        app.dependency_overrides.clear()

def test_list_webhook_subscriptions(mock_current_user):
    with patch("app.api.v1.endpoints.webhooks.get_current_user", return_value=mock_current_user), \
         patch("app.api.v1.endpoints.webhooks.get_db") as mock_get_db:

        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Override the dependency for the test client
        from app.api.deps import get_current_user, get_db
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        app.dependency_overrides[get_db] = lambda: mock_db

        import datetime
        dt = datetime.datetime.now(datetime.timezone.utc)
        sub1 = WebhookSubscription(
            id="sub-1", user_id="user-123", url="https://a.com", events=["a"], is_active=True, failure_count=0,
            created_at=dt, updated_at=dt
        )
        sub2 = WebhookSubscription(
            id="sub-2", user_id="user-123", url="https://b.com", events=["b"], is_active=False, failure_count=3,
            created_at=dt, updated_at=dt
        )

        mock_result = MagicMock()
        mock_result.scalars().all.return_value = [sub1, sub2]
        mock_db.execute.return_value = mock_result

        response = client.get("/api/v1/webhooks/subscriptions")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "sub-1"
        assert data[0]["url"] == "https://a.com"
        assert data[1]["id"] == "sub-2"
        assert data[1]["is_active"] is False

        mock_db.execute.assert_called_once()

        # Clean up overrides
        app.dependency_overrides.clear()
