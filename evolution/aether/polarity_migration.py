#!/usr/bin/env python3
"""
Polarity Migration Script

Migrates existing events from binary garbage flag to polarity spectrum.
Part of Sprint 1: Foundation of Feeling.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Make asyncpg optional for testing
try:
    import asyncpg
except ImportError:
    asyncpg = None

logger = logging.getLogger(__name__)


class PolarityMigration:
    """
    Handles migration from binary garbage flag to polarity spectrum.
    """
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool: Optional[asyncpg.Pool] = None
        self.stats = {
            'total_events': 0,
            'migrated': 0,
            'already_has_polarity': 0,
            'errors': 0
        }
    
    async def initialize(self):
        """Initialize database connection."""
        self.pool = await asyncpg.create_pool(self.db_url)
        
        # Create migration tracking table
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE SCHEMA IF NOT EXISTS evolution;
                
                CREATE TABLE IF NOT EXISTS evolution.polarity_migration (
                    migration_id SERIAL PRIMARY KEY,
                    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    completed_at TIMESTAMPTZ,
                    events_migrated INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'in_progress'
                );
            """)
    
    async def migrate_event_table(self) -> Dict[str, Any]:
        """
        Add polarity column to events table and migrate data.
        """
        async with self.pool.acquire() as conn:
            # Start migration tracking
            migration_id = await conn.fetchval("""
                INSERT INTO evolution.polarity_migration (started_at)
                VALUES (NOW())
                RETURNING migration_id;
            """)
            
            try:
                # Check if polarity column exists
                column_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_schema = 'public'
                        AND table_name = 'events'
                        AND column_name = 'polarity'
                    );
                """)
                
                if not column_exists:
                    # Add polarity column
                    await conn.execute("""
                        ALTER TABLE events 
                        ADD COLUMN polarity FLOAT DEFAULT 0.0 
                        CHECK (polarity >= -1.0 AND polarity <= 1.0);
                    """)
                    logger.info("Added polarity column to events table")
                
                # Migrate existing events
                result = await self._migrate_events_batch(conn)
                
                # Update migration record
                await conn.execute("""
                    UPDATE evolution.polarity_migration
                    SET completed_at = NOW(),
                        events_migrated = $1,
                        status = 'completed'
                    WHERE migration_id = $2;
                """, result['migrated'], migration_id)
                
                return result
                
            except Exception as e:
                # Mark migration as failed
                await conn.execute("""
                    UPDATE evolution.polarity_migration
                    SET status = 'failed',
                        completed_at = NOW()
                    WHERE migration_id = $1;
                """, migration_id)
                raise e
    
    async def _migrate_events_batch(self, conn) -> Dict[str, Any]:
        """
        Migrate events in batches.
        """
        batch_size = 1000
        total_migrated = 0
        
        while True:
            # Get batch of events with garbage flag but no polarity
            events = await conn.fetch("""
                SELECT id, garbage, type, agent, payload
                FROM events
                WHERE polarity IS NULL OR polarity = 0.0
                LIMIT $1;
            """, batch_size)
            
            if not events:
                break
            
            # Calculate polarity for each event
            updates = []
            for event in events:
                polarity = self._calculate_event_polarity(dict(event))
                updates.append((event['id'], polarity))
            
            # Batch update
            await conn.executemany("""
                UPDATE events SET polarity = $2 WHERE id = $1;
            """, updates)
            
            total_migrated += len(updates)
            logger.info(f"Migrated {len(updates)} events (total: {total_migrated})")
        
        return {'migrated': total_migrated}
    
    def _calculate_event_polarity(self, event: Dict[str, Any]) -> float:
        """
        Calculate polarity for an event.
        """
        # First check garbage flag
        if event.get('garbage'):
            return -0.8  # Garbage events get negative polarity
        
        # Base polarity by event type
        type_polarities = {
            'completion': 0.7,
            'success': 0.8,
            'created': 0.6,
            'error': -0.6,
            'failure': -0.8,
            'warning': -0.2
        }
        
        event_type = event.get('type', '')
        base_polarity = type_polarities.get(event_type, 0.3)
        
        # Adjust based on payload
        payload = event.get('payload', {})
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except:
                payload = {}
        
        if isinstance(payload, dict):
            # Check for success indicator
            if 'success' in payload:
                base_polarity = 0.8 if payload['success'] else -0.6
            
            # Check for errors
            if 'error' in payload or 'errors' in payload:
                base_polarity -= 0.3
        
        return max(-1.0, min(1.0, base_polarity))
    
    async def create_polarity_views(self):
        """
        Create database views for polarity analysis.
        """
        async with self.pool.acquire() as conn:
            # Quality distribution view
            await conn.execute("""
                CREATE OR REPLACE VIEW evolution.event_quality_distribution AS
                SELECT 
                    CASE 
                        WHEN polarity >= 0.8 THEN 'EXCELLENT'
                        WHEN polarity >= 0.5 THEN 'GOOD'
                        WHEN polarity >= 0.2 THEN 'ACCEPTABLE'
                        WHEN polarity >= -0.2 THEN 'NEUTRAL'
                        WHEN polarity >= -0.5 THEN 'POOR'
                        WHEN polarity >= -0.8 THEN 'CRITICAL'
                        ELSE 'FAILURE'
                    END as quality_band,
                    COUNT(*) as event_count,
                    AVG(polarity) as avg_polarity
                FROM events
                GROUP BY quality_band
                ORDER BY avg_polarity DESC;
            """)
            
            # Agent performance view
            await conn.execute("""
                CREATE OR REPLACE VIEW evolution.agent_polarity_performance AS
                SELECT 
                    agent,
                    COUNT(*) as total_events,
                    AVG(polarity) as avg_polarity,
                    MIN(polarity) as min_polarity,
                    MAX(polarity) as max_polarity,
                    STDDEV(polarity) as polarity_stddev,
                    COUNT(CASE WHEN polarity < 0 THEN 1 END) as negative_events,
                    COUNT(CASE WHEN polarity >= 0.5 THEN 1 END) as high_quality_events
                FROM events
                WHERE agent IS NOT NULL
                GROUP BY agent
                ORDER BY avg_polarity DESC;
            """)
            
            # Time-based polarity trends
            await conn.execute("""
                CREATE OR REPLACE VIEW evolution.polarity_trends AS
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour,
                    AVG(polarity) as avg_polarity,
                    COUNT(*) as event_count,
                    COUNT(CASE WHEN polarity < -0.5 THEN 1 END) as critical_count
                FROM events
                WHERE timestamp > NOW() - INTERVAL '7 days'
                GROUP BY hour
                ORDER BY hour DESC;
            """)
            
            logger.info("Created polarity analysis views")
    
    async def validate_migration(self) -> Dict[str, Any]:
        """
        Validate the migration results.
        """
        async with self.pool.acquire() as conn:
            # Check for events without polarity
            no_polarity = await conn.fetchval("""
                SELECT COUNT(*) FROM events 
                WHERE polarity IS NULL OR polarity = 0.0;
            """)
            
            # Get polarity distribution
            distribution = await conn.fetch("""
                SELECT 
                    quality_band,
                    event_count,
                    avg_polarity
                FROM evolution.event_quality_distribution;
            """)
            
            # Get agent performance
            agent_stats = await conn.fetch("""
                SELECT agent, avg_polarity, total_events
                FROM evolution.agent_polarity_performance
                LIMIT 10;
            """)
            
            return {
                'events_without_polarity': no_polarity,
                'quality_distribution': [
                    dict(row) for row in distribution
                ],
                'top_agents': [
                    dict(row) for row in agent_stats
                ],
                'migration_valid': no_polarity == 0
            }
    
    async def rollback_migration(self):
        """
        Rollback the migration if needed.
        """
        async with self.pool.acquire() as conn:
            # Remove polarity column
            await conn.execute("""
                ALTER TABLE events DROP COLUMN IF EXISTS polarity;
            """)
            
            # Drop views
            await conn.execute("""
                DROP VIEW IF EXISTS evolution.event_quality_distribution;
                DROP VIEW IF EXISTS evolution.agent_polarity_performance;
                DROP VIEW IF EXISTS evolution.polarity_trends;
            """)
            
            logger.info("Migration rolled back")
    
    async def close(self):
        """Close database connections."""
        if self.pool:
            await self.pool.close()


async def run_migration(db_url: str = "postgresql://localhost/cogplan"):
    """
    Run the polarity migration.
    """
    migration = PolarityMigration(db_url)
    
    try:
        # Initialize
        await migration.initialize()
        logger.info("🔄 Starting polarity migration...")
        
        # Run migration
        result = await migration.migrate_event_table()
        logger.info(f"✅ Migrated {result['migrated']} events")
        
        # Create analysis views
        await migration.create_polarity_views()
        
        # Validate
        validation = await migration.validate_migration()
        
        if validation['migration_valid']:
            logger.info("✅ Migration validated successfully!")
            logger.info(f"Quality distribution: {validation['quality_distribution']}")
        else:
            logger.warning(
                f"⚠️ {validation['events_without_polarity']} events still without polarity"
            )
        
        return validation
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        # Optionally rollback
        # await migration.rollback_migration()
        raise
    finally:
        await migration.close()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n🎈 Polarity Migration Script\n" + "="*50)
    print("This script will migrate events from garbage flag to polarity spectrum.")
    print("\nMigration steps:")
    print("1. Add polarity column to events table")
    print("2. Calculate polarity for existing events")
    print("3. Create analysis views")
    print("4. Validate migration")
    print("="*50)
    
    # Note: In production, would actually run the migration
    print("\n⚠️  Migration script ready but not executed (no database connection)")
    print("To run: asyncio.run(run_migration('your_db_url'))")
    print("\n✅ Migration script ready for Sprint 1!")