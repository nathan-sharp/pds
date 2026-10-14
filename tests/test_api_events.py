import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect
from unittest.mock import patch, MagicMock, AsyncMock

from app.main import app
from app.core.security import create_access_token
from app.core.events import dispatcher

client = TestClient(app)

def test_websocket_firehose_success():
    """Test successful connection and event receiving."""
    user_id = "test-user-id"
    token = create_access_token(subject=user_id, client_id="test_client")

    mock_user = MagicMock()
    mock_user.id = user_id

    with patch("app.api.v1.endpoints.events.get_user_from_token", new_callable=AsyncMock) as mock_get_user:
        mock_get_user.return_value = mock_user

        with client.websocket_connect(f"/api/v1/events/firehose?token={token}") as websocket:
            topic = f"user_{user_id}"
            callbacks = dispatcher._subscribers.get(topic, [])
            assert len(callbacks) == 1

def test_websocket_firehose_invalid_token():
    """Test connection with invalid token fails with 1008."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/api/v1/events/firehose?token=invalid_token") as websocket:
            websocket.receive_json()
    assert exc_info.value.code == 1008
