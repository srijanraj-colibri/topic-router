"""
core.schema
===========

Pydantic models defining the canonical event schema used by the
Alfresco → ActiveMQ → Python Event Router pipeline.

This module contains normalized, forward-compatible representations
of repository events emitted by Alfresco repository extensions.

Design goals:
- Strict but flexible validation
- Backward compatibility with evolving event producers
- Clear separation between transport schema and business logic
"""

from typing import Optional, Union
from pydantic import BaseModel, field_validator


class RepoEvent(BaseModel):
    # -------- Core envelope --------
    schemaVersion: int
    eventType: str
    timestamp: int

    # -------- Node identity --------
    nodeRef: str
    storeRef: str
    parentNodeRef: Optional[str] = None

    # -------- Path & naming --------
    name: Optional[str] = None
    path: Optional[str] = None

    # -------- Content metadata --------
    mimeType: Optional[str] = None
    size: Optional[int] = None
    encoding: Optional[str] = None
    versionLabel: Optional[str] = None

    # -------- Audit metadata --------
    creator: Optional[str] = None
    modifier: Optional[str] = None

    # Accept BOTH epoch millis and ISO strings
    createdAt: Optional[Union[int, str]] = None
    modifiedAt: Optional[Union[int, str]] = None

    # -------- Type info --------
    nodeType: Optional[str] = None


    # -------- Normalization (optional but clean) --------
    @field_validator("createdAt", "modifiedAt", mode="before")
    @classmethod
    def normalize_timestamps(cls, v):
        """
        Accept epoch millis or ISO strings.
        Keep as-is; consumers can normalize further.
        """
        if v is None:
            return None
        if isinstance(v, (int, str)):
            return v
        raise ValueError("Invalid timestamp format")

    class Config:
        extra = "ignore"
