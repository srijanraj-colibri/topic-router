"""
routes.autotag
==============

Routing rule for auto-tagging events.

This route forwards eligible repository events to the auto-tagging
processing queue. It explicitly excludes system-managed folders
to avoid recursive or internal processing.
"""

import logging

from core.base import BaseRoute
from core.schema import RepoEvent
from settings import settings

logger = logging.getLogger("router.route.autotag")


class AutoTagRoute(BaseRoute):
    """
    Auto-tagging route.

    Routes content-related events to the auto-tagging queue
    when they satisfy defined eligibility criteria.
    """

    @property
    def name(self) -> str:
        """
        Name of the route.

        Returns
        -------
        str
            Route identifier.
        """
        return "autotag"

    @property
    def queue(self) -> str:
        """
        Destination queue for auto-tagging.

        Returns
        -------
        str
            Queue name.
        """
        return settings.AUTOTAG_QUEUE

    def should_route(self, event: RepoEvent) -> bool:
        """
        Determine whether the event should be routed for auto-tagging.

        Criteria
        --------
        - Event type must be BINARY_CHANGED
        - Path must not belong to internal/system folders

        Parameters
        ----------
        event : RepoEvent
            Incoming repository event.

        Returns
        -------
        bool
            True if the event should be routed, otherwise False.
        """
        if not self._is_binary_changed(event):
            return False

        if self._is_system_path(event.path):
            return False

        logger.debug(
            "AutoTag route matched",
            extra={
                "eventType": event.eventType,
                "nodeRef": event.nodeRef,
                "path": event.path,
            },
        )
        return True

    @staticmethod
    def _is_binary_changed(event: RepoEvent) -> bool:
        """
        Check if the event represents a binary content change.

        Parameters
        ----------
        event : RepoEvent

        Returns
        -------
        bool
            True if event type is BINARY_CHANGED.
        """
        return event.eventType == "BINARY_CHANGED"

    @staticmethod
    def _is_system_path(path: str | None) -> bool:
        """
        Determine whether the path belongs to a system-managed folder.

        Parameters
        ----------
        path : str or None
            Repository path.

        Returns
        -------
        bool
            True if the path should be excluded.
        """
        if not path:
            return True

        excluded_prefixes = (
            "/Company Home/RULE_BASED_TAGS",
        )

        return any(path.startswith(prefix) for prefix in excluded_prefixes)
