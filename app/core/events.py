import asyncio
from typing import Callable, Dict, List, Any

# A callback is a callable taking a dictionary payload.
Callback = Callable[[Dict[str, Any]], Any]

class EventDispatcher:
    def __init__(self):
        self._subscribers: Dict[str, List[Callback]] = {}

    def subscribe(self, topic: str, callback: Callback) -> None:
        """Subscribe a callback to a specific topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

    async def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        """Publish an event payload to all subscribers of the topic."""
        if topic not in self._subscribers:
            return

        callbacks = self._subscribers[topic]
        if not callbacks:
            return

        # We handle async and sync callbacks.
        tasks = []
        for cb in callbacks:
            if asyncio.iscoroutinefunction(cb):
                tasks.append(asyncio.create_task(cb(payload)))
            else:
                # Run sync functions in a thread pool to avoid blocking the event loop
                tasks.append(asyncio.to_thread(cb, payload))

        if tasks:
            await asyncio.gather(*tasks)

# Global dispatcher instance
dispatcher = EventDispatcher()
