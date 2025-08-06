#!/usr/bin/env python3
"""Agent Runtime - Manages agent lifecycle and Kafka I/O."""
import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Type
import json

# Add parent paths for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from common.kafka_utils import get_kafka, KafkaIntegration

logger = logging.getLogger(__name__)


class AgentRuntime:
    """
    Runtime wrapper for Evolution agents.
    Handles spawning, Kafka I/O, health monitoring, and credit tracking.
    """
    
    def __init__(self, agent_class: Type, agent_id: str, config: Dict[str, Any] = None):
        """
        Initialize agent runtime.
        
        Args:
            agent_class: The agent class to instantiate
            agent_id: Unique identifier for this agent
            config: Agent configuration
        """
        self.agent_class = agent_class
        self.agent_id = agent_id
        self.config = config or {}
        
        # Kafka topics for this agent
        self.input_topic = f"{agent_id}-in"
        self.output_topic = f"{agent_id}-out"
        
        # Runtime state
        self.agent = None
        self.kafka = None
        self.consumer_id = None
        self.running = False
        self.health_check_task = None
        self.message_count = 0
        self.credit_usage = 0
        
        # Credit tracking
        self.credit_limit = self.config.get("credit_limit", 1000)
        self.credits_used = 0
    
    async def start(self):
        """Start the agent and wire up Kafka I/O."""
        logger.info(f"Starting agent runtime for {self.agent_id}")
        
        try:
            # Initialize agent instance
            self.agent = self.agent_class()
            logger.info(f"Initialized {self.agent_class.__name__}")
            
            # Initialize Kafka
            self.kafka = get_kafka()
            await self.kafka.start()
            
            # Create consumer for input topic
            self.consumer_id = await self.kafka.create_consumer(
                [self.input_topic],
                self._handle_message,
                f"{self.agent_id}-consumer"
            )
            
            if not self.consumer_id:
                raise RuntimeError(f"Failed to create consumer for {self.input_topic}")
            
            # Start consuming messages
            await self.kafka.start_consuming(self.consumer_id)
            
            # Start health check loop
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            self.running = True
            logger.info(f"Agent {self.agent_id} started successfully")
            
            # Publish startup event
            await self._publish_event({
                "type": "agent_started",
                "agent": self.agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "config": self.config
            })
            
        except Exception as e:
            logger.error(f"Failed to start agent {self.agent_id}: {e}")
            raise
    
    async def stop(self):
        """Stop the agent and clean up resources."""
        logger.info(f"Stopping agent {self.agent_id}")
        
        self.running = False
        
        # Cancel health check
        if self.health_check_task:
            self.health_check_task.cancel()
        
        # Publish shutdown event
        await self._publish_event({
            "type": "agent_stopped",
            "agent": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "messages_processed": self.message_count,
            "credits_used": self.credits_used
        })
        
        # Stop Kafka
        if self.kafka:
            await self.kafka.stop()
        
        logger.info(f"Agent {self.agent_id} stopped")
    
    async def _handle_message(self, message: Dict[str, Any]):
        """
        Handle incoming Kafka message.
        
        Args:
            message: Incoming message from Kafka
        """
        try:
            self.message_count += 1
            logger.debug(f"Agent {self.agent_id} processing message: {message.get('type')}")
            
            # Check credit limit
            if self.credits_used >= self.credit_limit:
                logger.warning(f"Agent {self.agent_id} exceeded credit limit")
                await self._publish_event({
                    "type": "credit_limit_exceeded",
                    "agent": self.agent_id,
                    "credits_used": self.credits_used,
                    "limit": self.credit_limit
                })
                return
            
            # Route message to appropriate agent method
            message_type = message.get("type", "unknown")
            response = await self._route_to_agent(message_type, message)
            
            # Track credit usage (simplified - would integrate with credit sentinel)
            message_credits = message.get("estimated_credits", 10)
            self.credits_used += message_credits
            
            # Publish response if generated
            if response:
                await self._publish_event(response)
            
        except Exception as e:
            logger.error(f"Error handling message in {self.agent_id}: {e}")
            await self._publish_event({
                "type": "error",
                "agent": self.agent_id,
                "error": str(e),
                "original_message": message
            })
    
    async def _route_to_agent(self, message_type: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Route message to appropriate agent method.
        
        Args:
            message_type: Type of message
            message: Full message data
            
        Returns:
            Response from agent or None
        """
        # Map message types to agent methods
        method_map = {
            "audit_request": "audit",
            "review_request": "review",
            "decision_request": "decide",
            "implementation_request": "implement",
            "financial_assessment": "assess_finances",
            "proposal": "process_proposal",
            "ping": "handle_ping"
        }
        
        method_name = method_map.get(message_type)
        
        if not method_name:
            logger.warning(f"Unknown message type for {self.agent_id}: {message_type}")
            return None
        
        # Check if agent has the method
        if not hasattr(self.agent, method_name):
            # Try common handler methods
            if hasattr(self.agent, "process_message"):
                return await self.agent.process_message(message)
            elif hasattr(self.agent, "handle"):
                return await self.agent.handle(message)
            else:
                logger.warning(f"Agent {self.agent_id} has no handler for {message_type}")
                return None
        
        # Call the agent method
        method = getattr(self.agent, method_name)
        result = await method(message)
        
        # Wrap result in standard envelope
        if result and not isinstance(result, dict):
            result = {"data": result}
        
        if result:
            result["agent"] = self.agent_id
            result["type"] = result.get("type", f"{message_type}_response")
            result["correlation_id"] = message.get("correlation_id")
            result["timestamp"] = datetime.utcnow().isoformat()
        
        return result
    
    async def _publish_event(self, event: Dict[str, Any]):
        """
        Publish event to output topic.
        
        Args:
            event: Event to publish
        """
        if not self.kafka:
            logger.warning(f"Cannot publish - Kafka not initialized for {self.agent_id}")
            return
        
        # Add agent metadata
        event["agent"] = self.agent_id
        event["timestamp"] = event.get("timestamp", datetime.utcnow().isoformat())
        
        # Publish to output topic
        success = await self.kafka.publish_event(self.output_topic, event)
        
        if success:
            logger.debug(f"Agent {self.agent_id} published: {event.get('type')}")
        else:
            logger.error(f"Agent {self.agent_id} failed to publish: {event.get('type')}")
    
    async def _health_check_loop(self):
        """Periodic health check loop."""
        while self.running:
            try:
                # Wait for health check interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Perform health check
                health = await self.get_health()
                
                # Publish health status
                await self._publish_event({
                    "type": "health_check",
                    "status": health["status"],
                    "metrics": health
                })
                
                logger.debug(f"Agent {self.agent_id} health: {health['status']}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for {self.agent_id}: {e}")
    
    async def get_health(self) -> Dict[str, Any]:
        """
        Get agent health status.
        
        Returns:
            Health status dictionary
        """
        kafka_health = await self.kafka.health_check() if self.kafka else {"status": "not_initialized"}
        
        return {
            "agent_id": self.agent_id,
            "status": "healthy" if self.running else "stopped",
            "running": self.running,
            "messages_processed": self.message_count,
            "credits_used": self.credits_used,
            "credit_limit": self.credit_limit,
            "credit_usage_percent": (self.credits_used / self.credit_limit * 100) if self.credit_limit > 0 else 0,
            "kafka": kafka_health,
            "uptime": "N/A"  # Would calculate from start time
        }
    
    async def run_forever(self):
        """Run the agent until interrupted."""
        logger.info(f"Agent {self.agent_id} running. Press Ctrl+C to stop.")
        
        # Set up signal handlers
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep running until stopped
        while self.running:
            await asyncio.sleep(1)
        
        logger.info(f"Agent {self.agent_id} exited")


class AgentSpawner:
    """
    Spawns and manages multiple agent runtimes.
    """
    
    def __init__(self):
        self.agents = {}
        
    async def spawn_agent(self, 
                          agent_class: Type,
                          agent_id: str,
                          config: Dict[str, Any] = None) -> AgentRuntime:
        """
        Spawn a new agent runtime.
        
        Args:
            agent_class: Agent class to instantiate
            agent_id: Unique agent ID
            config: Agent configuration
            
        Returns:
            AgentRuntime instance
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already exists")
            return self.agents[agent_id]
        
        runtime = AgentRuntime(agent_class, agent_id, config)
        await runtime.start()
        
        self.agents[agent_id] = runtime
        logger.info(f"Spawned agent: {agent_id}")
        
        return runtime
    
    async def stop_agent(self, agent_id: str):
        """Stop a specific agent."""
        if agent_id in self.agents:
            await self.agents[agent_id].stop()
            del self.agents[agent_id]
            logger.info(f"Stopped agent: {agent_id}")
    
    async def stop_all(self):
        """Stop all agents."""
        for agent_id in list(self.agents.keys()):
            await self.stop_agent(agent_id)
    
    async def get_all_health(self) -> Dict[str, Any]:
        """Get health status of all agents."""
        health = {}
        for agent_id, runtime in self.agents.items():
            health[agent_id] = await runtime.get_health()
        return health


# Example test agent for validation
class TestAgent:
    """Simple test agent for runtime validation."""
    
    async def handle_ping(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping message."""
        return {
            "type": "pong",
            "echo": message.get("data", ""),
            "agent_class": self.__class__.__name__
        }
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Generic message handler."""
        return {
            "type": "processed",
            "original_type": message.get("type"),
            "processed_at": datetime.utcnow().isoformat()
        }


# CLI for testing individual agents
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run an Evolution agent")
    parser.add_argument("--agent", default="test", help="Agent type to run")
    parser.add_argument("--id", help="Agent ID (defaults to agent type)")
    parser.add_argument("--config", help="JSON config file")
    args = parser.parse_args()
    
    async def main():
        # Load config if provided
        config = {}
        if args.config:
            with open(args.config) as f:
                config = json.load(f)
        
        # Determine agent class
        if args.agent == "test":
            agent_class = TestAgent
        else:
            # Would import actual agent classes here
            logger.error(f"Unknown agent type: {args.agent}")
            return
        
        # Create and run agent
        agent_id = args.id or args.agent
        runtime = AgentRuntime(agent_class, agent_id, config)
        
        await runtime.start()
        await runtime.run_forever()
    
    # Run the agent
    asyncio.run(main())