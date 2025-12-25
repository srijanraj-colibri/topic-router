"""
settings
========

Application configuration for the Alfresco Event Router.

Configuration values are loaded from environment variables using
Pydantic Settings. This module defines all runtime-tunable parameters
required to connect to ActiveMQ, configure routing behavior, and
control logging.

Design principles:
- Explicit configuration
- Fail fast on missing critical values
- Environment-first (12-factor app)
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.

    All values are loaded from environment variables by default.
    Field names map directly to environment variables.

    Example
    -------
    ACTIVEMQ_HOST=localhost
    ACTIVEMQ_PORT=61613
    EVENT_TOPIC=/topic/alfresco.upload.events
    """

    # ------------------------------------------------------------------
    # ActiveMQ connection
    # ------------------------------------------------------------------
    ACTIVEMQ_HOST: str = Field(
        default="localhost",
        description="ActiveMQ broker host",
    )
    ACTIVEMQ_PORT: int = Field(
        default=61613,
        description="ActiveMQ STOMP port",
    )
    ACTIVEMQ_USER: str = Field(
        default="admin",
        description="ActiveMQ username",
    )
    ACTIVEMQ_PASSWORD: str = Field(
        default="admin",
        description="ActiveMQ password",
        repr=False,
    )

    STOMP_HEARTBEAT_OUT: int = Field(
        default=10_000,
        description="Outgoing STOMP heartbeat interval (ms)",
    )
    STOMP_HEARTBEAT_IN: int = Field(
        default=10_000,
        description="Incoming STOMP heartbeat interval (ms)",
    )

    ACTIVEMQ_PREFETCH: int = Field(
        default=1,
        description="ActiveMQ prefetch size per consumer",
        ge=1,
    )

    # ------------------------------------------------------------------
    # Routing configuration
    # ------------------------------------------------------------------
    EVENT_TOPIC: str = Field(
        ...,
        description="Source topic for Alfresco repository events",
    )
    ROUTER_CLIENT_ID: str = Field(
        ...,
        description="Durable subscription client ID",
    )
    ROUTER_SUBSCRIPTION_NAME: str = Field(
        ...,
        description="Durable subscription name",
    )

    AUTOTAG_QUEUE: str = Field(
        ...,
        description="Destination queue for auto-tagging events",
    )
    
    SCORM_EXTRACTION_QUEUE: str = Field(
        ...,
        description="Destination queue for scorm detection and extraction events",
    )

    # Future extensions
    # AUTOMETA_QUEUE: str
    # VECTOR_QUEUE: str

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Application log level",
    )

    # ------------------------------------------------------------------
    # Pydantic configuration
    # ------------------------------------------------------------------
    model_config = {
        "extra": "ignore",
        "case_sensitive": True,
    }


# Singleton settings instance
settings = Settings()
