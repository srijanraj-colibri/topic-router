"""
core.base
=========

Abstract base definitions for event routing.

This module defines the contract that all routing implementations
must follow in the Python Event Router. Each route decides whether
an incoming repository event should be forwarded to a specific
destination queue and optionally transforms the payload.

Design principles:
- Explicit contracts via abstract base classes
- Separation of routing logic from transport concerns
- Extensible transformation hooks for future enrichment
"""

from abc import ABC, abstractmethod
from typing import Dict

from core.schema import RepoEvent


class BaseRoute(ABC):
    """
    Abstract base class for event routes.

    A route represents a single routing rule that:
    - Identifies itself by name
    - Targets a specific destination queue
    - Determines whether an event should be routed
    - Optionally transforms the event payload

    Concrete implementations are expected to be stateless and
    side-effect free.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of the route.

        Used for:
        - Logging
        - Metrics
        - Debugging
        - Observability

        Returns
        -------
        str
            Human-readable route name.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def queue(self) -> str:
        """
        Destination queue name.

        This value must match the queue configured in the
        message broker (e.g. ActiveMQ).

        Returns
        -------
        str
            Queue name.
        """
        raise NotImplementedError

    @abstractmethod
    def should_route(self, event: RepoEvent) -> bool:
        """
        Determine whether the given event should be routed.

        This method contains the routing predicate logic and
        must be deterministic and fast.

        Parameters
        ----------
        event : RepoEvent
            Incoming repository event.

        Returns
        -------
        bool
            True if the event should be routed to the destination
            queue, otherwise False.
        """
        raise NotImplementedError

    def transform(self, event: RepoEvent) -> Dict:
        """
        Transform the event payload before publishing.

        By default, this method returns the raw event model
        as a dictionary. Subclasses may override this method
        to enrich, filter, or reshape the payload.

        Examples
        --------
        - Add derived fields
        - Remove unused attributes
        - Normalize paths or metadata
        - Add routing hints

        Parameters
        ----------
        event : RepoEvent
            Incoming repository event.

        Returns
        -------
        dict
            Transformed event payload.
        """
        return event.model_dump(by_alias=True)
