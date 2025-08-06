"""Event envelope data model for SemLoop."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class EventType(str, Enum):
    """Event type categories."""
    TOOL_CALL = "tool_call"
    STATE_CHANGE = "state_change"
    COMPLETION = "completion"
    ERROR = "error"
    CHECKPOINT = "checkpoint"
    CREDIT_UPDATE = "credit_update"
    PR_CREATED = "pr_created"
    PR_MERGED = "pr_merged"
    TEST_RESULT = "test_result"
    METRICS_SNAPSHOT = "metrics_snapshot"


class EventMeta(BaseModel):
    """Event metadata."""
    session_id: str = Field(
        ...,
        pattern=r"^uma-v2-\d{4}-\d{2}-\d{2}-\d{1,4}$",
        description="Session identifier"
    )
    credits_used: Optional[int] = Field(
        None,
        ge=0,
        description="Credits consumed by this event"
    )
    context_hash: Optional[str] = Field(
        None,
        pattern=r"^sha256:[a-f0-9]{64}$",
        description="Context hash at time of event"
    )
    parent_event_id: Optional[UUID] = Field(
        None,
        description="ID of parent event if this is a child"
    )
    correlation_id: Optional[str] = Field(
        None,
        description="ID for correlating related events"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Optional tags for filtering/grouping"
    )


class EventEnvelope(BaseModel):
    """Standard event envelope for UMA-V2 agent events."""
    id: UUID = Field(
        ...,
        description="Unique event identifier (UUID v4)"
    )
    type: EventType = Field(
        ...,
        description="Event type category"
    )
    timestamp: datetime = Field(
        ...,
        description="ISO-8601 UTC timestamp when event occurred"
    )
    agent: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9-]*$",
        description="Name of agent that generated the event"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Event-specific data"
    )
    meta: EventMeta = Field(
        ...,
        description="Event metadata"
    )
    garbage: bool = Field(
        False,
        description="If true, embedder should ignore this event (marks low-quality/failed attempts)"
    )
    schema_version: str = Field(
        "1.1",
        pattern=r"^\d+\.\d+$",
        description="Schema version for forward compatibility"
    )
    
    @field_validator('agent')
    @classmethod
    def validate_agent_name(cls, v: str) -> str:
        """Ensure agent name follows convention."""
        if not v or not v[0].islower():
            raise ValueError("Agent name must start with lowercase letter")
        return v
    
    def mark_as_garbage(self) -> None:
        """Mark this event as garbage (low-quality/failed)."""
        self.garbage = True
    
    def is_high_quality(self) -> bool:
        """Check if this event should be processed for embeddings."""
        return not self.garbage
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }