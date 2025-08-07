
"""
@cognimap:fingerprint
id: f1b1e0c5-f78f-4ea4-9113-d57994399706
birth: 2025-08-07T07:23:38.072375Z
parent: None
intent: Embedder service for processing SemLoop events.
semantic_tags: [database, api, testing, service, model, configuration, security]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.072712Z
hash: b9561922
language: python
type: service
@end:cognimap
"""

"""Embedder service for processing SemLoop events."""
import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional, List
from uuid import UUID

from semloop_models import EventEnvelope


logger = logging.getLogger(__name__)


class EmbedderService:
    """Service for processing events and generating embeddings."""
    
    def __init__(self, 
                 kafka_consumer: Any,
                 vector_store: Any,
                 metrics_client: Optional[Any] = None):
        """Initialize embedder service.
        
        Args:
            kafka_consumer: Kafka/Redpanda consumer
            vector_store: Vector database client
            metrics_client: Optional metrics collector
        """
        self.consumer = kafka_consumer
        self.vector_store = vector_store
        self.metrics = metrics_client
        self.processed_count = 0
        self.skipped_garbage_count = 0
    
    async def process_event(self, event_data: Dict[str, Any]) -> bool:
        """Process a single event.
        
        Args:
            event_data: Raw event data from Kafka
            
        Returns:
            True if processed, False if skipped
        """
        try:
            # Parse event envelope
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            
            # Check garbage flag - this is the key immune system feature
            if event_data.get("garbage", False):
                logger.debug(f"Skipping garbage event: {event_data.get('id')}")
                self.skipped_garbage_count += 1
                
                if self.metrics:
                    self.metrics.increment("embedder.skipped_garbage")
                
                return False
            
            # Validate and create EventEnvelope
            event = EventEnvelope(**event_data)
            
            # Additional quality check using model method
            if not event.is_high_quality():
                logger.debug(f"Event marked as low quality: {event.id}")
                self.skipped_garbage_count += 1
                
                if self.metrics:
                    self.metrics.increment("embedder.skipped_low_quality")
                
                return False
            
            # Generate embedding (placeholder - would use actual model)
            embedding = await self._generate_embedding(event)
            
            # Store in vector database
            await self._store_embedding(event, embedding)
            
            self.processed_count += 1
            
            if self.metrics:
                self.metrics.increment("embedder.processed")
                self.metrics.gauge("embedder.total_processed", self.processed_count)
            
            logger.info(f"Processed event {event.id} from agent {event.agent}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            
            if self.metrics:
                self.metrics.increment("embedder.error")
            
            return False
    
    async def _generate_embedding(self, event: EventEnvelope) -> List[float]:
        """Generate embedding for event using sentence transformers.
        
        Args:
            event: Event envelope to embed
            
        Returns:
            Vector embedding from sentence transformer
        """
        # Combine relevant text from event
        text_parts = [
            f"Type: {event.type}",
            f"Agent: {event.agent}",
        ]
        
        # Add payload content (limited to avoid huge embeddings)
        payload_str = json.dumps(event.payload)
        if len(payload_str) > 1000:
            payload_str = payload_str[:1000] + "..."
        text_parts.append(f"Payload: {payload_str}")
        
        # Add metadata if present
        if event.meta and event.meta.tags:
            text_parts.append(f"Tags: {', '.join(event.meta.tags)}")
        
        text = " | ".join(text_parts)
        
        # Generate embedding using the selected method
        embedding_method = os.getenv("EMBEDDING_METHOD", "sentence-transformers")
        
        if embedding_method == "sentence-transformers":
            return await self._generate_sentence_transformer_embedding(text)
        elif embedding_method == "openai":
            return await self._generate_openai_embedding(text)
        else:
            # Fallback to simple hash-based embedding
            return await self._generate_hash_embedding(text)
    
    async def _generate_sentence_transformer_embedding(self, text: str) -> List[float]:
        """Generate embedding using sentence-transformers.
        
        This uses a lightweight model that can run locally.
        Default model: all-MiniLM-L6-v2 (384 dimensions)
        """
        try:
            # Lazy import to avoid dependency if not used
            from sentence_transformers import SentenceTransformer
            
            # Cache model to avoid reloading
            if not hasattr(self, '_sentence_model'):
                model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
                logger.info(f"Loading sentence transformer model: {model_name}")
                self._sentence_model = SentenceTransformer(model_name)
            
            # Generate embedding
            embedding = self._sentence_model.encode(text, convert_to_numpy=True)
            
            # Convert to list of floats
            return embedding.tolist()
            
        except ImportError:
            logger.warning("sentence-transformers not installed, falling back to hash embedding")
            return await self._generate_hash_embedding(text)
        except Exception as e:
            logger.error(f"Error generating sentence transformer embedding: {e}")
            return await self._generate_hash_embedding(text)
    
    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API.
        
        Requires OPENAI_API_KEY environment variable.
        Uses text-embedding-ada-002 (1536 dimensions)
        """
        try:
            # Lazy import
            import openai
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set, falling back to hash embedding")
                return await self._generate_hash_embedding(text)
            
            openai.api_key = api_key
            
            # Generate embedding
            response = await asyncio.to_thread(
                openai.Embedding.create,
                model="text-embedding-ada-002",
                input=text
            )
            
            return response["data"][0]["embedding"]
            
        except ImportError:
            logger.warning("openai not installed, falling back to hash embedding")
            return await self._generate_hash_embedding(text)
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}")
            return await self._generate_hash_embedding(text)
    
    async def _generate_hash_embedding(self, text: str) -> List[float]:
        """Generate a deterministic embedding using hashing.
        
        This is a fallback method that creates a pseudo-embedding
        using hash functions. Not as good as real embeddings but
        deterministic and doesn't require external dependencies.
        """
        import hashlib
        
        # Use multiple hash functions for different dimensions
        hashes = []
        for i in range(8):  # Generate 8 hash values
            h = hashlib.sha256(f"{i}:{text}".encode()).hexdigest()
            # Convert hex to float in range [-1, 1]
            value = (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1
            hashes.append(value)
        
        # Expand to 384 dimensions (matching MiniLM) by repeating with variations
        import math
        embedding = []
        for i in range(384):
            idx = i % len(hashes)
            # Add some variation based on position
            value = hashes[idx] * (1 + 0.1 * math.sin(i / 10))
            # Clip to [-1, 1] range
            value = max(-1.0, min(1.0, value))
            embedding.append(float(value))
        
        return embedding
    
    async def _store_embedding(self, event: EventEnvelope, embedding: list) -> None:
        """Store embedding in vector database.
        
        Args:
            event: Source event
            embedding: Generated embedding vector
        """
        # Store in vector database with metadata
        metadata = {
            "event_id": str(event.id),
            "event_type": event.type,
            "agent": event.agent,
            "timestamp": event.timestamp.isoformat(),
            "session_id": event.meta.session_id,
            "garbage": event.garbage,
            "embedding_dim": len(embedding),
            "embedding_method": os.getenv("EMBEDDING_METHOD", "sentence-transformers")
        }
        
        # Would call actual vector store here
        logger.debug(f"Stored embedding for event {event.id}")
    
    async def run(self) -> None:
        """Main processing loop."""
        logger.info("Embedder service starting...")
        
        while True:
            try:
                # Consume from Kafka/Redpanda
                message = await self.consumer.get_message()
                
                if message:
                    await self.process_event(message)
                else:
                    # No messages, sleep briefly
                    await asyncio.sleep(0.1)
                    
            except KeyboardInterrupt:
                logger.info("Embedder service shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"Embedder stats: {self.processed_count} processed, "
                   f"{self.skipped_garbage_count} garbage skipped")


# Placeholder consumer for testing
class MockKafkaConsumer:
    """Mock Kafka consumer for testing."""
    
    async def get_message(self) -> Optional[Dict[str, Any]]:
        """Get next message from queue."""
        await asyncio.sleep(0.1)
        return None


# Placeholder vector store for testing  
class MockVectorStore:
    """Mock vector store for testing."""
    
    async def insert(self, embedding: list, metadata: Dict[str, Any]) -> None:
        """Insert embedding with metadata."""
        pass