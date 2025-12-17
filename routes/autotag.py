import logging
from core.base import BaseRoute
from core.schema import RepoEvent
from settings import settings

logger = logging.getLogger("router.route.autotag")


class AutoTagRoute(BaseRoute):

    @property
    def name(self) -> str:
        return "autotag"

    @property
    def queue(self) -> str:
        return settings.AUTOTAG_QUEUE

    def should_route(self, event: RepoEvent) -> bool:
        decision = event.eventType == "CONTENT_READY"
        if decision:
            logger.debug("AutoTag matched for %s", event.nodeRef)
        return decision
