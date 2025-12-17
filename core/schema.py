from pydantic import BaseModel


class RepoEvent(BaseModel):
    nodeRef: str
    eventType: str   # CREATE | UPDATE | DELETE
