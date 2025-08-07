#!/usr/bin/env python3
"""
@cognimap:fingerprint
id: c15937fb-abe2-40ab-bbbf-0ca55bd60e80
birth: 2025-08-07T07:23:38.070865Z
parent: None
intent: Test real embeddings implementation.
semantic_tags: [api, testing, service, model, configuration, security]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.071068Z
hash: dcd250fa
language: python
type: test
@end:cognimap
"""

"""Test real embeddings implementation."""
import asyncio
import json
import os
from pathlib import Path
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from services.embedder import EmbedderService
from semloop_models import EventEnvelope


async def test_embeddings():
    """Test different embedding methods."""
    print("=" * 60)
    print("Testing Real Embeddings Implementation")
    print("=" * 60)
    
    # Create test event
    test_event = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "type": "tool_call",
        "timestamp": "2024-01-01T12:00:00Z",
        "agent": "planner",
        "payload": {
            "tool": "plan_creator",
            "action": "create",
            "result": "success",
            "description": "Created a comprehensive plan for API development"
        },
        "meta": {
            "session_id": "uma-v2-2024-01-01-001",
            "credits_used": 10,
            "tags": ["planning", "api", "development"]
        },
        "garbage": False
    }
    
    # Create embedder service
    embedder = EmbedderService(
        kafka_consumer=None,
        vector_store=None,
        metrics_client=None
    )
    
    print("\n1. Testing garbage flag filtering...")
    # Test garbage flag
    garbage_event = test_event.copy()
    garbage_event["garbage"] = True
    result = await embedder.process_event(garbage_event)
    assert result == False, "Garbage event should be skipped"
    print("   ✅ Garbage events correctly filtered")
    
    print("\n2. Testing embedding generation methods...")
    
    # Test hash embedding (always available)
    print("   Testing hash embedding...")
    os.environ["EMBEDDING_METHOD"] = "hash"
    event = EventEnvelope(**test_event)
    embedding = await embedder._generate_embedding(event)
    assert len(embedding) == 384, f"Expected 384 dimensions, got {len(embedding)}"
    assert all(isinstance(x, float) for x in embedding), "Embedding should be floats"
    assert all(-1 <= x <= 1 for x in embedding), "Values should be normalized"
    print(f"   ✅ Hash embedding: {len(embedding)} dimensions")
    
    # Test sentence-transformers if available
    try:
        import sentence_transformers
        print("   Testing sentence-transformers...")
        os.environ["EMBEDDING_METHOD"] = "sentence-transformers"
        
        # Clear cached model
        if hasattr(embedder, '_sentence_model'):
            delattr(embedder, '_sentence_model')
        
        embedding = await embedder._generate_embedding(event)
        assert len(embedding) == 384, f"Expected 384 dimensions, got {len(embedding)}"
        assert all(isinstance(x, float) for x in embedding), "Embedding should be floats"
        
        # Check that embeddings are different for different content
        event2 = EventEnvelope(**test_event)
        event2.payload = {"different": "content", "test": "value"}
        embedding2 = await embedder._generate_embedding(event2)
        
        # Calculate similarity (should be different)
        similarity = sum(a * b for a, b in zip(embedding, embedding2))
        assert similarity < 0.99, "Different content should have different embeddings"
        
        print(f"   ✅ Sentence-transformers: {len(embedding)} dimensions")
        print(f"      Similarity between different events: {similarity:.3f}")
        
    except ImportError:
        print("   ⚠️  sentence-transformers not installed (pip install sentence-transformers)")
    
    # Test OpenAI if API key is set
    if os.getenv("OPENAI_API_KEY"):
        try:
            import openai
            print("   Testing OpenAI embeddings...")
            os.environ["EMBEDDING_METHOD"] = "openai"
            embedding = await embedder._generate_embedding(event)
            assert len(embedding) == 1536, f"Expected 1536 dimensions, got {len(embedding)}"
            print(f"   ✅ OpenAI: {len(embedding)} dimensions")
        except ImportError:
            print("   ⚠️  openai not installed (pip install openai)")
    else:
        print("   ⚠️  OPENAI_API_KEY not set, skipping OpenAI test")
    
    print("\n3. Testing complete event processing...")
    os.environ["EMBEDDING_METHOD"] = "hash"  # Use hash for reliable testing
    embedder.processed_count = 0
    embedder.skipped_garbage_count = 0
    
    # Process valid event
    result = await embedder.process_event(test_event)
    assert result == True, "Valid event should be processed"
    assert embedder.processed_count == 1
    
    # Process garbage event
    result = await embedder.process_event(garbage_event)
    assert result == False, "Garbage event should be skipped"
    assert embedder.skipped_garbage_count == 1
    
    print(f"   ✅ Processed: {embedder.processed_count} events")
    print(f"   ✅ Filtered: {embedder.skipped_garbage_count} garbage events")
    
    print("\n4. Testing embedding consistency...")
    # Same input should produce same embedding
    embedding1 = await embedder._generate_embedding(event)
    embedding2 = await embedder._generate_embedding(event)
    assert embedding1 == embedding2, "Same input should produce same embedding"
    print("   ✅ Embeddings are deterministic")
    
    print("\n" + "=" * 60)
    print("✅ All embedding tests passed!")
    print("=" * 60)
    
    # Show configuration
    print("\nCurrent Configuration:")
    print(f"  EMBEDDING_METHOD: {os.getenv('EMBEDDING_METHOD', 'sentence-transformers')}")
    print(f"  Dimensions: {len(embedding1)}")
    print(f"  Method used: {embedder._generate_embedding.__name__}")
    
    return True


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(test_embeddings())
    if success:
        print("\n✅ Ready to use real embeddings in production!")
        print("\nTo install sentence-transformers:")
        print("  pip install sentence-transformers")
        print("\nTo use OpenAI embeddings:")
        print("  pip install openai")
        print("  export OPENAI_API_KEY=your-key-here")