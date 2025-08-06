#!/usr/bin/env python3
"""Kafka/Redpanda integration utilities for Evolution Engine."""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import os

# Using aiokafka for async Kafka operations
try:
    from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
    from aiokafka.errors import KafkaError
except ImportError:
    # Fallback for testing without aiokafka installed
    AIOKafkaProducer = None
    AIOKafkaConsumer = None
    KafkaError = Exception

logger = logging.getLogger(__name__)


class KafkaIntegration:
    """
    Kafka/Redpanda integration for Evolution Engine.
    Handles publishing and consuming events between agents.
    """
    
    def __init__(self, 
                 bootstrap_servers: str = None,
                 group_id: str = "evolution-engine",
                 enable_mock: bool = False):
        """
        Initialize Kafka integration.
        
        Args:
            bootstrap_servers: Kafka broker addresses
            group_id: Consumer group ID
            enable_mock: Use mock mode if aiokafka not available
        """
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )
        self.group_id = group_id
        self.enable_mock = enable_mock or (AIOKafkaProducer is None)
        
        self.producer = None
        self.consumers = {}
        self.mock_topics = {}  # For mock mode
        
        if self.enable_mock:
            logger.warning("Running in MOCK mode - no real Kafka connection")
    
    async def start(self):
        """Start Kafka producer and prepare for consumers."""
        if self.enable_mock:
            logger.info("Mock Kafka started")
            return
        
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            await self.producer.start()
            logger.info(f"Kafka producer started: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            self.enable_mock = True
            logger.warning("Falling back to MOCK mode")
    
    async def stop(self):
        """Stop all Kafka connections."""
        if self.enable_mock:
            return
        
        # Stop all consumers
        for consumer in self.consumers.values():
            await consumer.stop()
        
        # Stop producer
        if self.producer:
            await self.producer.stop()
        
        logger.info("Kafka connections closed")
    
    async def publish_event(self, 
                           topic: str, 
                           event: Dict[str, Any],
                           key: Optional[str] = None) -> bool:
        """
        Publish an event to a Kafka topic.
        
        Args:
            topic: Target topic name
            event: Event data to publish
            key: Optional partition key
            
        Returns:
            True if published successfully
        """
        # Add metadata
        event["timestamp"] = event.get("timestamp", datetime.utcnow().isoformat())
        event["topic"] = topic
        
        if self.enable_mock:
            # Mock mode - store in memory
            if topic not in self.mock_topics:
                self.mock_topics[topic] = []
            self.mock_topics[topic].append(event)
            logger.debug(f"[MOCK] Published to {topic}: {event.get('type', 'unknown')}")
            return True
        
        try:
            # Real Kafka publish
            await self.producer.send_and_wait(
                topic=topic,
                value=event,
                key=key
            )
            logger.debug(f"Published to {topic}: {event.get('type', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return False
    
    async def create_consumer(self, 
                            topics: List[str],
                            handler: Callable,
                            consumer_id: str = None) -> Optional[str]:
        """
        Create a consumer for specified topics.
        
        Args:
            topics: List of topics to consume
            handler: Async function to handle messages
            consumer_id: Unique ID for this consumer
            
        Returns:
            Consumer ID if successful
        """
        consumer_id = consumer_id or f"consumer_{len(self.consumers)}"
        
        if self.enable_mock:
            # Mock consumer - just store the handler
            self.consumers[consumer_id] = {
                "topics": topics,
                "handler": handler,
                "mock": True
            }
            logger.info(f"[MOCK] Consumer {consumer_id} created for {topics}")
            return consumer_id
        
        try:
            consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=f"{self.group_id}-{consumer_id}",
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            
            await consumer.start()
            
            self.consumers[consumer_id] = {
                "consumer": consumer,
                "handler": handler,
                "topics": topics,
                "task": None
            }
            
            logger.info(f"Consumer {consumer_id} started for topics: {topics}")
            return consumer_id
            
        except Exception as e:
            logger.error(f"Failed to create consumer: {e}")
            return None
    
    async def start_consuming(self, consumer_id: str):
        """
        Start consuming messages for a specific consumer.
        
        Args:
            consumer_id: ID of the consumer to start
        """
        if consumer_id not in self.consumers:
            logger.error(f"Consumer {consumer_id} not found")
            return
        
        consumer_info = self.consumers[consumer_id]
        
        if self.enable_mock:
            # Mock consuming - process any existing messages
            for topic in consumer_info["topics"]:
                if topic in self.mock_topics:
                    for event in self.mock_topics[topic]:
                        await consumer_info["handler"](event)
            return
        
        async def consume_loop():
            """Internal consumption loop."""
            consumer = consumer_info["consumer"]
            handler = consumer_info["handler"]
            
            try:
                async for msg in consumer:
                    try:
                        await handler(msg.value)
                    except Exception as e:
                        logger.error(f"Handler error: {e}")
            except asyncio.CancelledError:
                logger.info(f"Consumer {consumer_id} cancelled")
            except Exception as e:
                logger.error(f"Consumer {consumer_id} error: {e}")
        
        # Start consumption task
        consumer_info["task"] = asyncio.create_task(consume_loop())
        logger.info(f"Started consuming for {consumer_id}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check Kafka connection health.
        
        Returns:
            Health status dictionary
        """
        if self.enable_mock:
            return {
                "status": "healthy",
                "mode": "mock",
                "topics": list(self.mock_topics.keys()),
                "messages": sum(len(msgs) for msgs in self.mock_topics.values())
            }
        
        try:
            # Try to get cluster metadata
            if self.producer:
                metadata = await self.producer.client.fetch_all_metadata()
                return {
                    "status": "healthy",
                    "mode": "live",
                    "brokers": len(metadata.brokers),
                    "topics": len(metadata.topics),
                    "consumers": len(self.consumers)
                }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
        
        return {
            "status": "unhealthy",
            "error": str(e) if 'e' in locals() else "Unknown error"
        }
    
    # Convenience methods for common patterns
    
    async def request_reply(self,
                           request_topic: str,
                           reply_topic: str,
                           request: Dict[str, Any],
                           timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """
        Send a request and wait for reply pattern.
        
        Args:
            request_topic: Topic to send request
            reply_topic: Topic to listen for reply
            request: Request data
            timeout: Max wait time in seconds
            
        Returns:
            Reply data or None if timeout
        """
        # Add correlation ID
        import uuid
        correlation_id = str(uuid.uuid4())
        request["correlation_id"] = correlation_id
        
        # Set up reply listener
        reply_future = asyncio.Future()
        
        async def reply_handler(msg):
            if msg.get("correlation_id") == correlation_id:
                reply_future.set_result(msg)
        
        # Create temporary consumer for reply
        consumer_id = await self.create_consumer(
            [reply_topic],
            reply_handler,
            f"reply_{correlation_id}"
        )
        
        if not consumer_id:
            return None
        
        # Start consuming replies
        await self.start_consuming(consumer_id)
        
        # Send request
        await self.publish_event(request_topic, request)
        
        try:
            # Wait for reply with timeout
            reply = await asyncio.wait_for(reply_future, timeout=timeout)
            return reply
        except asyncio.TimeoutError:
            logger.warning(f"Request timeout for correlation_id: {correlation_id}")
            return None
        finally:
            # Clean up consumer
            if consumer_id in self.consumers:
                if not self.enable_mock:
                    consumer_info = self.consumers[consumer_id]
                    if consumer_info.get("task"):
                        consumer_info["task"].cancel()
                    if consumer_info.get("consumer"):
                        await consumer_info["consumer"].stop()
                del self.consumers[consumer_id]
    
    def get_mock_messages(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get messages from mock topic (for testing).
        
        Args:
            topic: Topic name
            
        Returns:
            List of messages
        """
        return self.mock_topics.get(topic, [])


# Singleton instance for easy import
_kafka_instance = None

def get_kafka() -> KafkaIntegration:
    """Get or create the global Kafka integration instance."""
    global _kafka_instance
    if _kafka_instance is None:
        _kafka_instance = KafkaIntegration()
    return _kafka_instance


# Example usage and testing
if __name__ == "__main__":
    async def test_kafka():
        """Test Kafka integration."""
        kafka = get_kafka()
        
        # Start Kafka
        await kafka.start()
        
        # Check health
        health = await kafka.health_check()
        print(f"Kafka health: {health}")
        
        # Test publish
        test_event = {
            "type": "test_event",
            "agent": "test_agent",
            "data": {"message": "Hello from Kafka integration"}
        }
        
        success = await kafka.publish_event("test-topic", test_event)
        print(f"Publish success: {success}")
        
        # Test consumer
        async def test_handler(msg):
            print(f"Received: {msg}")
        
        consumer_id = await kafka.create_consumer(
            ["test-topic"],
            test_handler,
            "test-consumer"
        )
        
        if consumer_id:
            await kafka.start_consuming(consumer_id)
            
            # Give it time to consume
            await asyncio.sleep(2)
        
        # Stop Kafka
        await kafka.stop()
        
        # Show mock messages if in mock mode
        if kafka.enable_mock:
            print(f"Mock messages: {kafka.get_mock_messages('test-topic')}")
    
    # Run test
    asyncio.run(test_kafka())