from abc import ABC, abstractmethod
from core.schema import RepoEvent


class BaseRoute(ABC):

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def queue(self) -> str: ...

    @abstractmethod
    def should_route(self, event: RepoEvent) -> bool: ...

    def transform(self, event: RepoEvent) -> dict:
        return event.model_dump()
