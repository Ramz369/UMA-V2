
"""
@cognimap:fingerprint
id: dace12d7-4a61-4791-8095-d117dc3d851f
birth: 2025-08-07T07:23:38.072307Z
parent: None
intent: SemLoop data models for event processing.
semantic_tags: [model, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.072327Z
hash: c614800e
language: python
type: model
@end:cognimap
"""

"""SemLoop data models for event processing."""
from .event_envelope import EventEnvelope, EventMeta, EventType

__all__ = [
    "EventEnvelope",
    "EventMeta", 
    "EventType"
]