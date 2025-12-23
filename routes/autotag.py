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
        decision = event.eventType == "BINARY_CHANGED" and (not event.path.startswith("/Company Home/RULE_BASED_TAGS"))
        
        if decision:
            logger.debug("AutoTag matched for %s", event.nodeRef)
        return decision
