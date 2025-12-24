"""
core.listener
=============

STOMP topic listener responsible for receiving repository events,
validating them, and routing them to downstream queues.

This listener implements a fail-safe message handling strategy:
- Invalid or unprocessable messages are ACKed and dropped
- Transient failures are NOT ACKed to allow redelivery
- Routing decisions are delegated to registered routes
"""

import json
import logging
from pydantic import ValidationError

from core.schema import RepoEvent
from core.registry import load_routes
from core.publisher import QueuePublisher

logger = logging.getLogger("router.listener")


class TopicRouterListener:
    """
    STOMP topic listener for repository events.

    This class receives messages from an ActiveMQ topic, validates
    the event schema, applies routing rules, and publishes derived
    payloads to destination queues.

    The listener follows an "ACK on success or discard" strategy
    to prevent poison-message loops.
    """


    def __init__(self, conn):
        self.conn = conn
        self.publisher = QueuePublisher(conn)
        self.routes = load_routes()
        logger.info("Loaded %d routes", len(self.routes))

    
    # ------------------------------------------------------------------
    # STOMP callbacks
    # ------------------------------------------------------------------
    def on_message(self, frame):
        """
        Handle an incoming STOMP message.

        Processing flow:
        1. Parse JSON payload
        2. Validate schema
        3. Apply routing rules
        4. Publish to queues
        5. ACK on success or safe discard

        Parameters
        ----------
        frame : Any
            STOMP frame containing headers and message body.
        """
        ack_id = frame.headers.get("ack")
        sub_id = frame.headers.get("subscription")

        try:
            # Direct JSON parsing
            raw_data = json.loads(frame.body)

            # Schema validation
            event = RepoEvent.model_validate(raw_data)

            logger.info(
                "Event received",
                extra={
                    "eventType": event.eventType,
                    "nodeRef": event.nodeRef,
                    "path": event.path,
                },
            )
            
            if event.eventType != "BINARY_CHANGED":
                logger.info("Ignoring eventType=%s", event.eventType)

                # ignoring other events as of now (please make changes as needed based on future extensions)
                self.conn.send_frame(
                    "ACK",
                    headers={"id": ack_id, "subscription": sub_id},
                )
                return
            
            for route in self.routes:
                if route.should_route(event):
                    payload = route.transform(event)
                    self.publisher.publish(route.queue, payload)
                else:
                    logger.info("Ignoring eventType=%s path=%s" , event.eventType, event.path)

            # ACK only after full success
            self.conn.send_frame(
                "ACK",
                headers={"id": ack_id, "subscription": sub_id},
            )

        except json.JSONDecodeError as e:
            # ❌ Invalid JSON → ACK & drop
            logger.error("Invalid JSON payload, ACK & drop", exc_info=e)
            self.conn.send_frame(
                "ACK",
                headers={"id": ack_id, "subscription": sub_id},
            )

        except ValidationError as e:
            # ❌ Schema mismatch → ACK & drop
            logger.error("Invalid event schema, ACK & drop", exc_info=e)
            self.conn.send_frame(
                "ACK",
                headers={"id": ack_id, "subscription": sub_id},
            )

        except Exception:
            # 🔁 Any other failure → NO ACK (redelivery)
            logger.exception("Router failure, NO ACK (redelivery)")

    def on_heartbeat_timeout(self):
        logger.warning("STOMP heartbeat timeout detected")

    def on_disconnected(self):
        logger.warning("Disconnected from ActiveMQ broker")
