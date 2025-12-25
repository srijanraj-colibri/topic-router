"""
routes.scorm_extraction
======================

Routing rule for SCORM extraction events.

This route forwards eligible repository events to the SCORM extraction
processing queue. It performs only cheap routing checks and defers
SCORM validation to downstream consumers.
"""

import logging


from core.base import BaseRoute
from core.schema import RepoEvent
from settings import settings

logger = logging.getLogger("router.route.scorm_extraction")


class SCORMExtractionRoute(BaseRoute):
    """
    SCORM Extraction route.

    Routes ZIP-based binary change events to the SCORM extraction queue.
    """

    @property
    def name(self) -> str:
        """Route identifier."""
        return "scorm_extraction"

    @property
    def queue(self) -> str:
        """Destination queue for SCORM extraction."""
        return settings.SCORM_EXTRACTION_QUEUE

    def should_route(self, event: RepoEvent) -> bool:
        """
        Determine whether the event should be routed for SCORM extraction.

        Criteria
        --------
        - Event type must be BINARY_CHANGED
        - Path must not be system-managed
        - File must be a .zip (SCORM validation happens downstream)
        """
        if not self._is_binary_changed(event):
            return False

        if self._is_system_path(event.path):
            return False

        if not self._is_zip_file(event.path):
            return False

        logger.debug(
            "SCORM ZIP route matched",
            extra={
                "eventType": event.eventType,
                "nodeRef": event.nodeRef,
                "path": event.path,
            },
        )
        return True

    @staticmethod
    def _is_binary_changed(event: RepoEvent) -> bool:
        """Check if the event represents a binary content change."""
        return event.eventType == "BINARY_CHANGED"

    @staticmethod
    def _is_zip_file(path: str | None) -> bool:
        """Check whether the path points to a ZIP file."""
        if not path:
            return False
        return path.lower().endswith(".zip")

    @staticmethod
    def _is_system_path(path: str | None) -> bool:
        """Exclude system-managed folders."""
        if not path:
            return True

        excluded_prefixes = (
            "/Company Home/RULE_BASED_TAGS",
        )

        return any(path.startswith(prefix) for prefix in excluded_prefixes)
    
