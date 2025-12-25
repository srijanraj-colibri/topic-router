"""
core.publisher
==============

Message publishing utilities for routing events to destination queues.

This module provides a thin abstraction over the STOMP connection
used by the router to publish transformed event payloads to
ActiveMQ queues.

Design principles:
- Minimal logic at the transport layer
- No business or routing decisions
- Explicit, JSON-only payloads
"""

import json

class QueuePublisher:
    """
    Queue message publisher.

    Responsible for serializing payloads and sending them to
    destination queues using an active STOMP connection.
    """
    def __init__(self, conn):
        """
        Initialize the queue publisher.

        Parameters
        ----------
        conn : Any
            Active STOMP connection instance.
        """
        self.conn = conn

    def publish(self, destination: str, payload: dict):
        """
        Publish a message to a queue.

        Parameters
        ----------
        destination : str
            Queue name.
        payload : dict
            Message payload to publish. Must be JSON-serializable.

        Raises
        ------
        TypeError
            If the payload cannot be serialized to JSON.
        """
        self.conn.send(
            destination=destination,
            body=json.dumps(payload),
            headers={
                "persistent": "true",
                "content-type": "application/json",
            },
        )
