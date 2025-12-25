"""
main
====

Application entry point for the Alfresco Event Router.

This module is responsible for:
- Initializing logging
- Establishing the STOMP connection
- Subscribing to the event topic
- Managing application lifecycle and graceful shutdown
"""

import logging
import signal
import sys
import time
from typing import Optional

import stomp

from settings import settings
from core.listener import TopicRouterListener
from core.logging_config import setup_logging

logger = logging.getLogger("router.main")

_shutdown_requested: bool = False


def _handle_shutdown(signum, frame) -> None:
    """
    Handle termination signals.

    Parameters
    ----------
    signum : int
        Signal number.
    frame : frame
        Current stack frame.
    """
    global _shutdown_requested
    logger.warning("Shutdown signal received", extra={"signal": signum})
    _shutdown_requested = True


def _create_connection() -> stomp.Connection12:
    """
    Create and configure a STOMP connection.

    Returns
    -------
    stomp.Connection12
        Configured STOMP connection.
    """
    return stomp.Connection12(
        [(settings.ACTIVEMQ_HOST, settings.ACTIVEMQ_PORT)],
        heartbeats=(
            settings.STOMP_HEARTBEAT_OUT,
            settings.STOMP_HEARTBEAT_IN,
        ),
    )


def main() -> None:
    """
    Application entry point.
    """
    setup_logging(settings.LOG_LEVEL)

    logger.info("Starting Alfresco Event Router")

    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    conn: Optional[stomp.Connection12] = None

    try:
        conn = _create_connection()
        conn.set_listener("", TopicRouterListener(conn))

        conn.connect(
            login=settings.ACTIVEMQ_USER,
            passcode=settings.ACTIVEMQ_PASSWORD,
            wait=True,
            headers={
                "client-id": settings.ROUTER_CLIENT_ID,
            },
        )

        logger.info(
            "Connected to ActiveMQ",
            extra={
                "host": settings.ACTIVEMQ_HOST,
                "port": settings.ACTIVEMQ_PORT,
            },
        )

        conn.subscribe(
            destination=settings.EVENT_TOPIC,
            id=settings.ROUTER_SUBSCRIPTION_NAME,
            ack="client-individual",
            headers={
                "activemq.subscriptionName": settings.ROUTER_SUBSCRIPTION_NAME,
                "activemq.prefetchSize": str(settings.ACTIVEMQ_PREFETCH),
            },
        )

        logger.info(
            "Subscribed to topic",
            extra={
                "topic": settings.EVENT_TOPIC,
                "subscription": settings.ROUTER_SUBSCRIPTION_NAME,
                "prefetch": settings.ACTIVEMQ_PREFETCH,
            },
        )
        while not _shutdown_requested:
            time.sleep(1)

    except Exception:
        logger.exception("Fatal router error")
        sys.exit(1)

    finally:
        if conn and conn.is_connected():
            logger.info("Disconnecting from ActiveMQ")
            conn.disconnect()

        logger.info("Event router stopped cleanly")


if __name__ == "__main__":
    main()
