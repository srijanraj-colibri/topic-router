import time
import stomp
import logging

from settings import settings
from core.listener import TopicRouterListener
from core.logging_config import setup_logging


def main():
    setup_logging(settings.LOG_LEVEL)

    logger = logging.getLogger("router.main")
    logger.info("Starting Alfresco Event Router")

    conn = stomp.Connection12(
        [(settings.ACTIVEMQ_HOST, settings.ACTIVEMQ_PORT)],
        heartbeats=(settings.STOMP_HEARTBEAT_OUT, settings.STOMP_HEARTBEAT_IN),
    )
    
    conn.set_listener("", TopicRouterListener(conn))

    conn.connect(
        login=settings.ACTIVEMQ_USER,
        passcode=settings.ACTIVEMQ_PASSWORD,
        wait=True,
        headers={
            "client-id": settings.ROUTER_CLIENT_ID
        }
    )

    logger.info(
        "Subscribed to topic",
        extra={
            "topic": settings.EVENT_TOPIC,
            "subscription": settings.ROUTER_SUBSCRIPTION_NAME,
        },
    )

    conn.subscribe(
        destination=settings.EVENT_TOPIC,
        id=settings.ROUTER_SUBSCRIPTION_NAME,  # better than "router-1"
        ack="client-individual",
        headers={
            "activemq.subscriptionName": settings.ROUTER_SUBSCRIPTION_NAME,
            "activemq.prefetchSize": str(settings.ACTIVEMQ_PREFETCH),
        },
    )

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
