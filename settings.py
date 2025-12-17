from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ---------- ActiveMQ ----------
    ACTIVEMQ_HOST: str = Field(default="localhost")
    ACTIVEMQ_PORT: int = Field(default=61613)
    ACTIVEMQ_USER: str = Field(default="admin")
    ACTIVEMQ_PASSWORD: str = Field(default="admin")

    STOMP_HEARTBEAT_OUT: int = 10000
    STOMP_HEARTBEAT_IN: int = 10000
    ACTIVEMQ_PREFETCH: int = 1

    # ---------- Routing ----------
    EVENT_TOPIC: str
    ROUTER_CLIENT_ID: str
    ROUTER_SUBSCRIPTION_NAME: str

    AUTOTAG_QUEUE: str
    # future:
    # AUTOMETA_QUEUE: str
    # VECTOR_QUEUE: str

    LOG_LEVEL: str = "INFO"

    model_config = {"extra": "ignore"}


settings = Settings()
