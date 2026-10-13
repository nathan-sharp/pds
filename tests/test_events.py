import pytest
import asyncio
from app.core.events import EventDispatcher

@pytest.mark.asyncio
async def test_event_dispatcher_subscribe_publish():
    dispatcher = EventDispatcher()

    received_payloads = []

    async def async_callback(payload):
        received_payloads.append(payload)

    def sync_callback(payload):
        received_payloads.append(payload)

    # Subscribe to 'test_topic'
    dispatcher.subscribe("test_topic", async_callback)
    dispatcher.subscribe("test_topic", sync_callback)

    # Subscribe to another topic
    dispatcher.subscribe("other_topic", async_callback)

    # Publish to 'test_topic'
    await dispatcher.publish("test_topic", {"key": "value"})

    # Check if both callbacks received the payload
    assert len(received_payloads) == 2
    assert received_payloads[0] == {"key": "value"}
    assert received_payloads[1] == {"key": "value"}

    # Publish to 'other_topic'
    await dispatcher.publish("other_topic", {"another": "data"})

    assert len(received_payloads) == 3
    assert received_payloads[2] == {"another": "data"}

@pytest.mark.asyncio
async def test_event_dispatcher_no_subscribers():
    dispatcher = EventDispatcher()
    # Should not raise any errors
    await dispatcher.publish("empty_topic", {"data": "nothing"})
