
"""
@cognimap:fingerprint
id: ef146e83-572f-4cd0-865b-b3e8b5bdf43c
birth: 2025-08-07T07:23:38.062664Z
parent: None
intent: Tests for garbage flag functionality.
semantic_tags: [testing, service, model, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.063008Z
hash: da184075
language: python
type: test
@end:cognimap
"""

"""Tests for garbage flag functionality."""
import json
import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from semloop_models import EventEnvelope, EventMeta, EventType
from services.embedder import EmbedderService


class TestEventEnvelopeGarbageFlag:
    """Test garbage flag in EventEnvelope model."""
    
    def test_default_garbage_false(self):
        """Test that garbage defaults to False."""
        event = EventEnvelope(
            id=uuid4(),
            type=EventType.TOOL_CALL,
            timestamp=datetime.utcnow(),
            agent="test-agent",
            payload={"test": "data"},
            meta=EventMeta(session_id="uma-v2-2024-01-01-001")
        )
        
        assert event.garbage is False
        assert event.is_high_quality() is True
    
    def test_explicit_garbage_true(self):
        """Test setting garbage to True."""
        event = EventEnvelope(
            id=uuid4(),
            type=EventType.ERROR,
            timestamp=datetime.utcnow(),
            agent="test-agent",
            payload={"error": "failure"},
            meta=EventMeta(session_id="uma-v2-2024-01-01-001"),
            garbage=True
        )
        
        assert event.garbage is True
        assert event.is_high_quality() is False
    
    def test_mark_as_garbage_method(self):
        """Test mark_as_garbage method."""
        event = EventEnvelope(
            id=uuid4(),
            type=EventType.TOOL_CALL,
            timestamp=datetime.utcnow(),
            agent="test-agent",
            payload={"test": "data"},
            meta=EventMeta(session_id="uma-v2-2024-01-01-001")
        )
        
        assert event.garbage is False
        event.mark_as_garbage()
        assert event.garbage is True
        assert event.is_high_quality() is False
    
    def test_schema_version_default(self):
        """Test schema version defaults to 1.1."""
        event = EventEnvelope(
            id=uuid4(),
            type=EventType.TOOL_CALL,
            timestamp=datetime.utcnow(),
            agent="test-agent",
            payload={"test": "data"},
            meta=EventMeta(session_id="uma-v2-2024-01-01-001")
        )
        
        assert event.schema_version == "1.1"
    
    def test_json_serialization_with_garbage(self):
        """Test JSON serialization includes garbage flag."""
        event = EventEnvelope(
            id=uuid4(),
            type=EventType.ERROR,
            timestamp=datetime.utcnow(),
            agent="test-agent",
            payload={"error": "test"},
            meta=EventMeta(session_id="uma-v2-2024-01-01-001"),
            garbage=True
        )
        
        json_str = event.model_dump_json()
        data = json.loads(json_str)
        
        assert "garbage" in data
        assert data["garbage"] is True
        assert data["schema_version"] == "1.1"


class TestEmbedderServiceGarbageHandling:
    """Test embedder service garbage event handling."""
    
    @pytest.fixture
    def embedder(self):
        """Create embedder service with mocks."""
        consumer = MagicMock()
        vector_store = MagicMock()
        metrics = MagicMock()
        
        return EmbedderService(
            kafka_consumer=consumer,
            vector_store=vector_store,
            metrics_client=metrics
        )
    
    @pytest.mark.asyncio
    async def test_skip_garbage_event(self, embedder):
        """Test that garbage events are skipped."""
        garbage_event = {
            "id": str(uuid4()),
            "type": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "test-agent",
            "payload": {"error": "bad data"},
            "meta": {"session_id": "uma-v2-2024-01-01-001"},
            "garbage": True
        }
        
        result = await embedder.process_event(garbage_event)
        
        assert result is False
        assert embedder.skipped_garbage_count == 1
        assert embedder.processed_count == 0
        embedder.metrics.increment.assert_called_with("embedder.skipped_garbage")
    
    @pytest.mark.asyncio
    async def test_process_non_garbage_event(self, embedder):
        """Test that non-garbage events are processed."""
        good_event = {
            "id": str(uuid4()),
            "type": "tool_call",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "test-agent",
            "payload": {"tool": "test", "result": "success"},
            "meta": {"session_id": "uma-v2-2024-01-01-001"},
            "garbage": False
        }
        
        # Mock the embedding generation
        with patch.object(embedder, '_generate_embedding', 
                         return_value=[0.0] * 1536) as mock_gen:
            with patch.object(embedder, '_store_embedding') as mock_store:
                result = await embedder.process_event(good_event)
        
        assert result is True
        assert embedder.processed_count == 1
        assert embedder.skipped_garbage_count == 0
        embedder.metrics.increment.assert_called_with("embedder.processed")
        mock_gen.assert_called_once()
        mock_store.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_default_garbage_false_processed(self, embedder):
        """Test events without garbage flag are processed."""
        event_no_flag = {
            "id": str(uuid4()),
            "type": "completion",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "test-agent",
            "payload": {"status": "complete"},
            "meta": {"session_id": "uma-v2-2024-01-01-001"}
            # Note: no garbage field
        }
        
        with patch.object(embedder, '_generate_embedding', 
                         return_value=[0.0] * 1536):
            with patch.object(embedder, '_store_embedding'):
                result = await embedder.process_event(event_no_flag)
        
        assert result is True
        assert embedder.processed_count == 1
        assert embedder.skipped_garbage_count == 0
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, embedder):
        """Test metrics are properly tracked."""
        # Process mix of garbage and good events
        events = [
            {"garbage": True},
            {"garbage": False},
            {"garbage": True},
            {"garbage": False},
            {}  # No flag = good
        ]
        
        for i, event_partial in enumerate(events):
            event = {
                "id": str(uuid4()),
                "type": "tool_call",
                "timestamp": datetime.utcnow().isoformat(),
                "agent": "test-agent",
                "payload": {"index": i},
                "meta": {"session_id": "uma-v2-2024-01-01-001"},
                **event_partial
            }
            
            with patch.object(embedder, '_generate_embedding', 
                             return_value=[0.0] * 1536):
                with patch.object(embedder, '_store_embedding'):
                    await embedder.process_event(event)
        
        assert embedder.skipped_garbage_count == 2
        assert embedder.processed_count == 3
        
        # Check metrics calls
        assert embedder.metrics.increment.call_count > 0
        garbage_calls = [
            call for call in embedder.metrics.increment.call_args_list
            if call[0][0] == "embedder.skipped_garbage"
        ]
        assert len(garbage_calls) == 2


class TestSchemaValidation:
    """Test JSON schema validation with garbage flag."""
    
    def test_schema_accepts_garbage_field(self):
        """Test that schema accepts garbage field."""
        import jsonschema
        
        # Load the schema
        with open("schemas/event_envelope.schema.json") as f:
            schema = json.load(f)
        
        # Valid event with garbage flag
        event = {
            "id": str(uuid4()),
            "type": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "test-agent",
            "payload": {"error": "test"},
            "meta": {"session_id": "uma-v2-2024-01-01-001"},
            "garbage": True,
            "schema_version": "1.1"
        }
        
        # Should not raise
        jsonschema.validate(event, schema)
    
    def test_schema_works_without_garbage(self):
        """Test that schema still works without garbage field."""
        import jsonschema
        
        with open("schemas/event_envelope.schema.json") as f:
            schema = json.load(f)
        
        # Valid event without garbage flag
        event = {
            "id": str(uuid4()),
            "type": "tool_call",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "test-agent",
            "payload": {"tool": "test"},
            "meta": {"session_id": "uma-v2-2024-01-01-001"}
        }
        
        # Should not raise
        jsonschema.validate(event, schema)
    
    def test_example_has_garbage_field(self):
        """Test that at least one example includes garbage field."""
        with open("schemas/event_envelope.schema.json") as f:
            schema = json.load(f)
        
        # Check first example has garbage field
        assert "examples" in schema
        assert len(schema["examples"]) > 0
        assert "garbage" in schema["examples"][0]
        assert schema["examples"][0]["garbage"] is False