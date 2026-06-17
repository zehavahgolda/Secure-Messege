"""
broadcaster.py — Real-time message broadcasting for SSE clients.

This module manages subscriptions from connected clients and publishes
messages to all of them instantly when a new message arrives.

Architecture:
  - Maintains a queue for each connected SSE client
  - When POST /messages is called, broadcasts to all queues
  - SSE /stream endpoint subscribes and listens to its queue
  - Messages flow: send_message() → broadcaster.publish() → all queues
"""

import asyncio
from typing import Any


class Broadcaster:
    """
    Central hub for broadcasting messages to all connected SSE clients.
    
    Each client that connects to GET /stream gets its own asyncio.Queue.
    When a message is published, it's added to all queues.
    Clients receive messages in real-time by listening to their queue.
    """
    
    def __init__(self):
        self.subscribers: list[asyncio.Queue[dict[str, Any]]] = []
    
    async def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        """
        Register a new SSE client.
        Returns a queue that this client will listen to.
        """
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.subscribers.append(queue)
        return queue
    
    async def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        """
        Unregister an SSE client (when they disconnect).
        """
        self.subscribers.remove(queue)
    
    async def publish(self, message: dict[str, Any]) -> None:
        """
        Broadcast a message to all connected clients.
        
        Each subscriber's queue receives the message.
        Clients read from their queue and send via SSE.
        """
        for queue in self.subscribers:
            await queue.put(message)


# Global broadcaster instance — shared across all requests
broadcaster = Broadcaster()
