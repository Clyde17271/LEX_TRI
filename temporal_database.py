"""
Temporal Database Integration for LEX TRI

This module provides database integration for the LEX TRI temporal agent,
supporting PostgreSQL with tri-temporal data models, AGI capabilities,
and hive swarm coordination.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import UUID, uuid4
import logging

import asyncpg
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import numpy as np

# Import temporal components
from temporal_viz import TemporalPoint, TemporalTimeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemporalDatabase:
    """Database interface for LEX TRI temporal data management."""

    def __init__(self, database_url: str):
        """Initialize database connection."""
        self.database_url = database_url
        self.engine = None
        self.async_engine = None
        self.session_factory = None

    async def initialize(self):
        """Initialize database connections and ensure schema exists."""
        try:
            # Create async engine for high-performance operations
            self.async_engine = create_async_engine(
                self.database_url.replace('postgresql://', 'postgresql+asyncpg://'),
                echo=False,
                pool_size=20,
                max_overflow=30
            )

            # Create sync engine for migrations and admin operations
            self.engine = create_engine(self.database_url)

            # Create session factory
            self.session_factory = sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Ensure schema is initialized
            await self._ensure_schema()

            logger.info("Temporal database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def _ensure_schema(self):
        """Ensure database schema exists and is up to date."""
        try:
            async with self.async_engine.begin() as conn:
                # Check if schemas exist
                result = await conn.execute(text("""
                    SELECT schema_name FROM information_schema.schemata
                    WHERE schema_name IN ('temporal', 'agi', 'hive', 'analytics')
                """))
                existing_schemas = [row[0] for row in result.fetchall()]

                if len(existing_schemas) < 4:
                    logger.info("Database schema incomplete, initializing...")

                    # Read and execute schema file
                    schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schemas', 'temporal_schema.sql')
                    if os.path.exists(schema_path):
                        with open(schema_path, 'r') as f:
                            schema_sql = f.read()

                        # Execute schema creation
                        await conn.execute(text(schema_sql))
                        logger.info("Database schema initialized")
                    else:
                        logger.warning(f"Schema file not found: {schema_path}")

        except Exception as e:
            logger.error(f"Failed to ensure schema: {e}")
            raise

    async def store_temporal_event(self, temporal_point: TemporalPoint,
                                 timeline_id: Optional[UUID] = None,
                                 event_type: str = "system_event",
                                 event_source: str = "lextri") -> UUID:
        """Store a temporal event in the database."""
        try:
            async with self.session_factory() as session:
                event_id = uuid4()

                # Insert the temporal event
                await session.execute(text("""
                    INSERT INTO temporal.events (
                        event_id, valid_time_start, transaction_time, decision_time,
                        event_type, event_source, event_data, metadata
                    ) VALUES (
                        :event_id, :valid_time, :transaction_time, :decision_time,
                        :event_type, :event_source, :event_data, :metadata
                    )
                """), {
                    'event_id': event_id,
                    'valid_time': temporal_point.valid_time,
                    'transaction_time': temporal_point.transaction_time,
                    'decision_time': temporal_point.decision_time,
                    'event_type': event_type,
                    'event_source': event_source,
                    'event_data': json.dumps(temporal_point.event_data),
                    'metadata': json.dumps({
                        'event_id': temporal_point.event_id,
                        'source': 'temporal_viz'
                    })
                })

                # Link to timeline if specified
                if timeline_id:
                    await session.execute(text("""
                        INSERT INTO temporal.timeline_events (timeline_id, event_id)
                        VALUES (:timeline_id, :event_id)
                    """), {
                        'timeline_id': timeline_id,
                        'event_id': event_id
                    })

                await session.commit()
                logger.info(f"Stored temporal event: {event_id}")
                return event_id

        except Exception as e:
            logger.error(f"Failed to store temporal event: {e}")
            raise

    async def store_timeline(self, timeline: TemporalTimeline) -> UUID:
        """Store a complete temporal timeline in the database."""
        try:
            async with self.session_factory() as session:
                timeline_id = uuid4()

                # Insert the timeline
                await session.execute(text("""
                    INSERT INTO temporal.timelines (
                        timeline_id, name, description, start_time, timeline_type
                    ) VALUES (
                        :timeline_id, :name, :description, :start_time, :timeline_type
                    )
                """), {
                    'timeline_id': timeline_id,
                    'name': timeline.name,
                    'description': getattr(timeline, 'description', 'Timeline from temporal_viz'),
                    'start_time': min(point.valid_time for point in timeline.points),
                    'timeline_type': 'imported'
                })

                # Store all temporal points
                for sequence_number, point in enumerate(timeline.points):
                    event_id = await self.store_temporal_event(
                        point, timeline_id,
                        event_type=point.event_data.get('event_type', 'timeline_event')
                    )

                    # Update sequence number
                    await session.execute(text("""
                        UPDATE temporal.timeline_events
                        SET sequence_number = :seq
                        WHERE timeline_id = :timeline_id AND event_id = :event_id
                    """), {
                        'seq': sequence_number,
                        'timeline_id': timeline_id,
                        'event_id': event_id
                    })

                await session.commit()
                logger.info(f"Stored timeline with {len(timeline.points)} events: {timeline_id}")
                return timeline_id

        except Exception as e:
            logger.error(f"Failed to store timeline: {e}")
            raise

    async def load_timeline(self, timeline_id: UUID) -> TemporalTimeline:
        """Load a temporal timeline from the database."""
        try:
            async with self.session_factory() as session:
                # Load timeline metadata
                timeline_result = await session.execute(text("""
                    SELECT name, description, start_time, end_time
                    FROM temporal.timelines
                    WHERE timeline_id = :timeline_id
                """), {'timeline_id': timeline_id})

                timeline_row = timeline_result.fetchone()
                if not timeline_row:
                    raise ValueError(f"Timeline not found: {timeline_id}")

                # Load temporal events
                events_result = await session.execute(text("""
                    SELECT e.event_id, e.valid_time_start, e.transaction_time,
                           e.decision_time, e.event_type, e.event_data, te.sequence_number
                    FROM temporal.events e
                    JOIN temporal.timeline_events te ON e.event_id = te.event_id
                    WHERE te.timeline_id = :timeline_id
                    ORDER BY te.sequence_number, e.valid_time_start
                """), {'timeline_id': timeline_id})

                # Convert to TemporalPoint objects
                points = []
                for row in events_result.fetchall():
                    event_data = json.loads(row[5]) if row[5] else {}
                    point = TemporalPoint(
                        valid_time=row[1],
                        transaction_time=row[2],
                        decision_time=row[3],
                        event_data=event_data,
                        event_id=str(row[0])
                    )
                    points.append(point)

                # Create timeline
                timeline = TemporalTimeline(
                    name=timeline_row[0],
                    points=points
                )
                timeline.description = timeline_row[1]

                logger.info(f"Loaded timeline {timeline_id} with {len(points)} events")
                return timeline

        except Exception as e:
            logger.error(f"Failed to load timeline: {e}")
            raise

    async def get_anomalies(self, timeline_id: Optional[UUID] = None,
                          severity: Optional[str] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve temporal anomalies from the database."""
        try:
            async with self.session_factory() as session:
                query = """
                    SELECT a.anomaly_id, a.event_id, a.anomaly_type, a.severity,
                           a.confidence, a.description, a.detected_at, a.status,
                           e.valid_time_start, e.transaction_time, e.decision_time
                    FROM temporal.anomalies a
                    JOIN temporal.events e ON a.event_id = e.event_id
                """

                params = {'limit': limit}
                conditions = []

                if timeline_id:
                    query += " JOIN temporal.timeline_events te ON e.event_id = te.event_id"
                    conditions.append("te.timeline_id = :timeline_id")
                    params['timeline_id'] = timeline_id

                if severity:
                    conditions.append("a.severity = :severity")
                    params['severity'] = severity

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                query += " ORDER BY a.detected_at DESC LIMIT :limit"

                result = await session.execute(text(query), params)

                anomalies = []
                for row in result.fetchall():
                    anomalies.append({
                        'anomaly_id': str(row[0]),
                        'event_id': str(row[1]),
                        'anomaly_type': row[2],
                        'severity': row[3],
                        'confidence': float(row[4]),
                        'description': row[5],
                        'detected_at': row[6],
                        'status': row[7],
                        'temporal_data': {
                            'valid_time': row[8],
                            'transaction_time': row[9],
                            'decision_time': row[10]
                        }
                    })

                logger.info(f"Retrieved {len(anomalies)} anomalies")
                return anomalies

        except Exception as e:
            logger.error(f"Failed to get anomalies: {e}")
            raise

    async def register_agi_agent(self, name: str, agent_type: str,
                               capabilities: List[str],
                               config: Dict[str, Any] = None) -> UUID:
        """Register an AGI agent in the database."""
        try:
            async with self.session_factory() as session:
                agent_id = uuid4()

                await session.execute(text("""
                    INSERT INTO agi.agents (
                        agent_id, name, agent_type, capabilities, config, status
                    ) VALUES (
                        :agent_id, :name, :agent_type, :capabilities, :config, 'active'
                    )
                """), {
                    'agent_id': agent_id,
                    'name': name,
                    'agent_type': agent_type,
                    'capabilities': json.dumps(capabilities),
                    'config': json.dumps(config or {})
                })

                await session.commit()
                logger.info(f"Registered AGI agent: {agent_id}")
                return agent_id

        except Exception as e:
            logger.error(f"Failed to register AGI agent: {e}")
            raise

    async def store_conversation(self, agent_id: UUID, messages: List[Dict[str, Any]],
                               title: str = None) -> UUID:
        """Store an AGI conversation."""
        try:
            async with self.session_factory() as session:
                conversation_id = uuid4()

                # Insert conversation
                await session.execute(text("""
                    INSERT INTO agi.conversations (
                        conversation_id, agent_id, title, context_type
                    ) VALUES (
                        :conversation_id, :agent_id, :title, 'temporal_analysis'
                    )
                """), {
                    'conversation_id': conversation_id,
                    'agent_id': agent_id,
                    'title': title or f"Conversation {datetime.now().isoformat()}"
                })

                # Insert messages
                for message in messages:
                    await session.execute(text("""
                        INSERT INTO agi.messages (
                            conversation_id, role, content, content_type, metadata
                        ) VALUES (
                            :conversation_id, :role, :content, :content_type, :metadata
                        )
                    """), {
                        'conversation_id': conversation_id,
                        'role': message.get('role', 'user'),
                        'content': message.get('content', ''),
                        'content_type': message.get('content_type', 'text'),
                        'metadata': json.dumps(message.get('metadata', {}))
                    })

                await session.commit()
                logger.info(f"Stored conversation: {conversation_id}")
                return conversation_id

        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            raise

    async def register_hive_node(self, name: str, node_type: str,
                               host_address: str, port: int,
                               capabilities: List[str]) -> UUID:
        """Register a node in the hive swarm."""
        try:
            async with self.session_factory() as session:
                node_id = uuid4()

                await session.execute(text("""
                    INSERT INTO hive.nodes (
                        node_id, name, node_type, host_address, port, capabilities, status
                    ) VALUES (
                        :node_id, :name, :node_type, :host_address, :port, :capabilities, 'active'
                    )
                """), {
                    'node_id': node_id,
                    'name': name,
                    'node_type': node_type,
                    'host_address': host_address,
                    'port': port,
                    'capabilities': json.dumps(capabilities)
                })

                await session.commit()
                logger.info(f"Registered hive node: {node_id}")
                return node_id

        except Exception as e:
            logger.error(f"Failed to register hive node: {e}")
            raise

    async def create_hive_task(self, task_type: str, input_data: Dict[str, Any],
                             priority: int = 5, parent_task_id: UUID = None) -> UUID:
        """Create a task in the hive swarm."""
        try:
            async with self.session_factory() as session:
                task_id = uuid4()

                await session.execute(text("""
                    INSERT INTO hive.tasks (
                        task_id, task_type, priority, parent_task_id, input_data, status
                    ) VALUES (
                        :task_id, :task_type, :priority, :parent_task_id, :input_data, 'pending'
                    )
                """), {
                    'task_id': task_id,
                    'task_type': task_type,
                    'priority': priority,
                    'parent_task_id': parent_task_id,
                    'input_data': json.dumps(input_data)
                })

                await session.commit()
                logger.info(f"Created hive task: {task_id}")
                return task_id

        except Exception as e:
            logger.error(f"Failed to create hive task: {e}")
            raise

    async def get_swarm_health(self) -> Dict[str, Any]:
        """Get the health status of the hive swarm."""
        try:
            async with self.session_factory() as session:
                result = await session.execute(text("""
                    SELECT * FROM hive.calculate_swarm_health()
                """))

                health_data = result.fetchone()
                if health_data:
                    return {
                        'total_nodes': health_data[0],
                        'active_nodes': health_data[1],
                        'health_percentage': float(health_data[2]),
                        'average_load': float(health_data[3]) if health_data[3] else 0.0,
                        'timestamp': datetime.now(timezone.utc)
                    }
                else:
                    return {
                        'total_nodes': 0,
                        'active_nodes': 0,
                        'health_percentage': 0.0,
                        'average_load': 0.0,
                        'timestamp': datetime.now(timezone.utc)
                    }

        except Exception as e:
            logger.error(f"Failed to get swarm health: {e}")
            raise

    async def store_metric(self, metric_name: str, metric_type: str,
                         value: Union[float, str, Dict[str, Any]],
                         source_component: str = "lextri",
                         tags: Dict[str, Any] = None):
        """Store a system metric."""
        try:
            async with self.session_factory() as session:
                metric_data = {
                    'metric_name': metric_name,
                    'metric_type': metric_type,
                    'source_component': source_component,
                    'tags': json.dumps(tags or {})
                }

                # Set appropriate value field based on type
                if isinstance(value, (int, float)):
                    metric_data['numeric_value'] = float(value)
                elif isinstance(value, str):
                    metric_data['text_value'] = value
                else:
                    metric_data['json_value'] = json.dumps(value)

                await session.execute(text("""
                    INSERT INTO analytics.metrics (
                        metric_name, metric_type, source_component, tags,
                        numeric_value, text_value, json_value
                    ) VALUES (
                        :metric_name, :metric_type, :source_component, :tags,
                        :numeric_value, :text_value, :json_value
                    )
                """), metric_data)

                await session.commit()

        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
            raise

    async def close(self):
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")


# Global database instance
_db_instance: Optional[TemporalDatabase] = None

async def get_database() -> TemporalDatabase:
    """Get the global database instance."""
    global _db_instance

    if _db_instance is None:
        database_url = os.getenv('DATABASE_URL',
                                'postgresql://lextri_user:lextri_secure_password@localhost:5432/lextri_temporal')
        _db_instance = TemporalDatabase(database_url)
        await _db_instance.initialize()

    return _db_instance

async def initialize_database(database_url: str = None) -> TemporalDatabase:
    """Initialize the database with a specific URL."""
    global _db_instance

    if database_url is None:
        database_url = os.getenv('DATABASE_URL',
                                'postgresql://lextri_user:lextri_secure_password@localhost:5432/lextri_temporal')

    _db_instance = TemporalDatabase(database_url)
    await _db_instance.initialize()
    return _db_instance