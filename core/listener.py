import logging
from pydantic import ValidationError

from core.schema import RepoEvent
from core.registry import load_routes
from core.publisher import QueuePublisher
from core.parsers import parse_alfresco_event

logger = logging.getLogger("router.listener")


class TopicRouterListener:

    def __init__(self, conn):
        self.conn = conn
        self.publisher = QueuePublisher(conn)
        self.routes = load_routes()
        logger.info("Loaded %d routes", len(self.routes))

    def on_message(self, frame):
        ack_id = frame.headers.get("ack")
        sub_id = frame.headers.get("subscription")

        try:
            raw_data = parse_alfresco_event(frame.body)
            event = RepoEvent.model_validate(raw_data)

            logger.info(
                "Event received",
                extra={
                    "eventType": event.eventType,
                    "nodeRef": event.nodeRef,
                },
            )

            for route in self.routes:
                if route.should_route(event):
                    payload = route.transform(event)
                    self.publisher.publish(route.queue, payload)

            # ACK only after successful routing
            self.conn.send_frame(
                "ACK",
                headers={"id": ack_id, "subscription": sub_id},
            )

        except ValidationError as e:
            logger.error("Invalid event payload, ACK & drop", exc_info=e)
            self.conn.send_frame(
                "ACK",
                headers={"id": ack_id, "subscription": sub_id},
            )

        except Exception:
            logger.exception("Router failure, NO ACK (redelivery)")
    
    def on_heartbeat_timeout(self):
        logger.warning("STOMP heartbeat timeout detected")

    def on_disconnected(self):
        logger.warning("Disconnected from ActiveMQ broker")
