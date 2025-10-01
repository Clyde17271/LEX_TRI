"""
AGI Hive Swarm System for LEX TRI

This module implements a distributed AGI system that coordinates multiple AI agents
in a hive-like swarm to provide enhanced temporal analysis capabilities. The system
includes consensus mechanisms, task distribution, and collective intelligence.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Any, Callable
from uuid import UUID, uuid4
from dataclasses import dataclass
from enum import Enum
import aiohttp
import websockets
from rich.console import Console

# Import AI libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from langchain.llms import OpenAI
    from langchain.agents import AgentType, initialize_agent
    from langchain.tools import Tool
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

# Import temporal components
from temporal_viz import TemporalPoint, TemporalTimeline
from temporal_database import get_database, TemporalDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeStatus(Enum):
    """Hive node status."""
    JOINING = "joining"
    ACTIVE = "active"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"

@dataclass
class HiveTask:
    """Represents a task in the hive swarm."""
    task_id: UUID
    task_type: str
    priority: int
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None
    status: TaskStatus = TaskStatus.PENDING
    assigned_node_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    progress_percentage: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

@dataclass
class HiveNode:
    """Represents a node in the hive swarm."""
    node_id: UUID
    name: str
    node_type: str
    host_address: str
    port: int
    capabilities: List[str]
    status: NodeStatus = NodeStatus.JOINING
    current_load: float = 0.0
    total_tasks_completed: int = 0
    last_heartbeat: datetime = None

    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now(timezone.utc)

class AGIAgent:
    """Individual AGI agent within the hive system."""

    def __init__(self, agent_id: UUID, name: str, agent_type: str,
                 capabilities: List[str], config: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.config = config or {}
        self.status = "active"
        self.conversation_history: List[Dict[str, Any]] = []

        # Initialize AI client based on configuration
        self._init_ai_client()

    def _init_ai_client(self):
        """Initialize the appropriate AI client."""
        primary_model = self.config.get('primary_model', 'gpt-4')

        if primary_model.startswith('gpt') and HAS_OPENAI:
            self.ai_client = openai.OpenAI(
                api_key=self.config.get('openai_api_key')
            )
            self.client_type = 'openai'
        elif primary_model.startswith('claude') and HAS_ANTHROPIC:
            self.ai_client = anthropic.Anthropic(
                api_key=self.config.get('anthropic_api_key')
            )
            self.client_type = 'anthropic'
        else:
            logger.warning(f"No suitable AI client available for {primary_model}")
            self.ai_client = None
            self.client_type = 'mock'

    async def process_temporal_analysis(self, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process temporal analysis task."""
        try:
            if self.client_type == 'openai' and self.ai_client:
                response = await self._openai_temporal_analysis(timeline_data)
            elif self.client_type == 'anthropic' and self.ai_client:
                response = await self._anthropic_temporal_analysis(timeline_data)
            else:
                response = await self._mock_temporal_analysis(timeline_data)

            return {
                'analysis': response,
                'agent_id': str(self.agent_id),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'confidence': 0.85
            }

        except Exception as e:
            logger.error(f"Agent {self.name} failed temporal analysis: {e}")
            return {
                'error': str(e),
                'agent_id': str(self.agent_id),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    async def _openai_temporal_analysis(self, timeline_data: Dict[str, Any]) -> str:
        """Perform temporal analysis using OpenAI."""
        prompt = f"""
        Analyze the following temporal data for anomalies and patterns:

        Timeline Data: {json.dumps(timeline_data, indent=2)}

        Please provide:
        1. Identified temporal anomalies
        2. Pattern analysis across VT/TT/DT dimensions
        3. Potential causes and remediation steps
        4. Confidence assessment

        Focus on tri-temporal relationships and inconsistencies.
        """

        response = self.ai_client.chat.completions.create(
            model=self.config.get('primary_model', 'gpt-4'),
            messages=[
                {"role": "system", "content": "You are LEX TRI, a temporal debugging expert specializing in Valid Time, Transaction Time, and Decision Time analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    async def _anthropic_temporal_analysis(self, timeline_data: Dict[str, Any]) -> str:
        """Perform temporal analysis using Anthropic Claude."""
        prompt = f"""
        Analyze the following temporal data for anomalies and patterns:

        Timeline Data: {json.dumps(timeline_data, indent=2)}

        Please provide:
        1. Identified temporal anomalies
        2. Pattern analysis across VT/TT/DT dimensions
        3. Potential causes and remediation steps
        4. Confidence assessment

        Focus on tri-temporal relationships and inconsistencies.
        """

        response = self.ai_client.messages.create(
            model=self.config.get('primary_model', 'claude-3-sonnet-20240229'),
            max_tokens=2000,
            system="You are LEX TRI, a temporal debugging expert specializing in Valid Time, Transaction Time, and Decision Time analysis.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text

    async def _mock_temporal_analysis(self, timeline_data: Dict[str, Any]) -> str:
        """Mock temporal analysis for testing."""
        return f"""
        Mock Analysis by {self.name}:

        1. Temporal Anomalies Detected: 2
           - Time travel detected in event sequence
           - Ingestion lag of 45 seconds identified

        2. Pattern Analysis:
           - VT/TT alignment: 85% consistent
           - DT timing: Premature decisions detected in 3 events

        3. Recommendations:
           - Review event ingestion pipeline
           - Implement temporal validation checks
           - Add decision delay mechanisms

        4. Confidence: 85%

        Data points analyzed: {len(timeline_data.get('points', []))}
        """

class HiveCoordinator:
    """Coordinates the AGI hive swarm for distributed temporal analysis."""

    def __init__(self, swarm_size: int = 3, coordinator_port: int = 9000):
        self.swarm_size = swarm_size
        self.coordinator_port = coordinator_port
        self.nodes: Dict[UUID, HiveNode] = {}
        self.agents: Dict[UUID, AGIAgent] = {}
        self.task_queue: List[HiveTask] = []
        self.active_tasks: Dict[UUID, HiveTask] = {}
        self.completed_tasks: List[HiveTask] = []
        self.db: Optional[TemporalDatabase] = None
        self.consensus_threshold = 0.7
        self.running = False

    async def initialize(self):
        """Initialize the hive coordinator."""
        try:
            # Initialize database connection
            self.db = await get_database()

            # Register coordinator as a hive node
            coordinator_node_id = await self.db.register_hive_node(
                name="HiveCoordinator",
                node_type="coordinator",
                host_address="localhost",
                port=self.coordinator_port,
                capabilities=["coordination", "consensus", "task_distribution"]
            )

            console.print(f"[green]Hive Coordinator initialized with ID: {coordinator_node_id}[/green]")

            # Initialize AGI agents
            await self._initialize_agents()

            logger.info("Hive coordinator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize hive coordinator: {e}")
            raise

    async def _initialize_agents(self):
        """Initialize AGI agents for the swarm."""
        agent_configs = [
            {
                'name': 'TemporalAnalyst-Alpha',
                'agent_type': 'temporal_analyzer',
                'capabilities': ['temporal_analysis', 'anomaly_detection', 'pattern_recognition'],
                'primary_model': 'gpt-4'
            },
            {
                'name': 'TemporalAnalyst-Beta',
                'agent_type': 'temporal_analyzer',
                'capabilities': ['temporal_analysis', 'data_validation', 'recommendation_engine'],
                'primary_model': 'claude-3-sonnet'
            },
            {
                'name': 'TemporalAnalyst-Gamma',
                'agent_type': 'temporal_synthesizer',
                'capabilities': ['consensus_building', 'result_synthesis', 'confidence_assessment'],
                'primary_model': 'gpt-4'
            }
        ]

        for config in agent_configs[:self.swarm_size]:
            agent_id = uuid4()

            # Register in database
            await self.db.register_agi_agent(
                name=config['name'],
                agent_type=config['agent_type'],
                capabilities=config['capabilities'],
                config=config
            )

            # Create agent instance
            agent = AGIAgent(
                agent_id=agent_id,
                name=config['name'],
                agent_type=config['agent_type'],
                capabilities=config['capabilities'],
                config=config
            )

            self.agents[agent_id] = agent
            console.print(f"[blue]Initialized AGI agent: {config['name']}[/blue]")

    async def submit_temporal_analysis_task(self, timeline: TemporalTimeline,
                                          priority: int = 5) -> UUID:
        """Submit a temporal analysis task to the hive swarm."""
        try:
            # Convert timeline to database format
            timeline_id = await self.db.store_timeline(timeline)

            # Create hive task
            task_id = await self.db.create_hive_task(
                task_type="temporal_analysis",
                input_data={
                    'timeline_id': str(timeline_id),
                    'timeline_data': timeline.to_dict(),
                    'analysis_type': 'comprehensive'
                },
                priority=priority
            )

            # Create task object
            task = HiveTask(
                task_id=task_id,
                task_type="temporal_analysis",
                priority=priority,
                input_data={
                    'timeline_id': str(timeline_id),
                    'timeline_data': timeline.to_dict()
                }
            )

            self.task_queue.append(task)
            console.print(f"[yellow]Submitted temporal analysis task: {task_id}[/yellow]")

            # Trigger task processing
            asyncio.create_task(self._process_task_queue())

            return task_id

        except Exception as e:
            logger.error(f"Failed to submit temporal analysis task: {e}")
            raise

    async def _process_task_queue(self):
        """Process pending tasks in the queue."""
        if not self.task_queue:
            return

        # Sort by priority (higher numbers = higher priority)
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)

        while self.task_queue and len(self.active_tasks) < len(self.agents):
            task = self.task_queue.pop(0)

            # Assign to available agent
            available_agents = [
                agent for agent in self.agents.values()
                if agent.status == "active" and not any(
                    active_task.assigned_node_id == agent.agent_id
                    for active_task in self.active_tasks.values()
                )
            ]

            if available_agents:
                agent = available_agents[0]
                task.assigned_node_id = agent.agent_id
                task.status = TaskStatus.ASSIGNED
                self.active_tasks[task.task_id] = task

                # Process task asynchronously
                asyncio.create_task(self._execute_task(task, agent))

    async def _execute_task(self, task: HiveTask, agent: AGIAgent):
        """Execute a task with the assigned agent."""
        try:
            task.status = TaskStatus.RUNNING
            console.print(f"[cyan]Agent {agent.name} starting task {task.task_id}[/cyan]")

            # Process the task based on type
            if task.task_type == "temporal_analysis":
                result = await agent.process_temporal_analysis(task.input_data['timeline_data'])
                task.output_data = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(timezone.utc)
                task.progress_percentage = 100

                console.print(f"[green]Task {task.task_id} completed by {agent.name}[/green]")

            # Move to completed tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            self.completed_tasks.append(task)

            # Check if this completes a consensus group
            await self._check_consensus_completion(task)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_data = {'error': str(e), 'agent_id': str(agent.agent_id)}
            logger.error(f"Task {task.task_id} failed: {e}")

            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]

    async def _check_consensus_completion(self, completed_task: HiveTask):
        """Check if enough agents have completed analysis for consensus."""
        timeline_id = completed_task.input_data.get('timeline_id')
        if not timeline_id:
            return

        # Find all completed tasks for this timeline
        related_tasks = [
            task for task in self.completed_tasks
            if (task.task_type == "temporal_analysis" and
                task.input_data.get('timeline_id') == timeline_id and
                task.status == TaskStatus.COMPLETED)
        ]

        # Check if we have enough for consensus
        if len(related_tasks) >= max(2, int(len(self.agents) * self.consensus_threshold)):
            consensus_result = await self._build_consensus(related_tasks)

            # Store consensus result
            await self._store_consensus_result(timeline_id, consensus_result, related_tasks)

            console.print(f"[bold green]Consensus reached for timeline {timeline_id}[/bold green]")

    async def _build_consensus(self, tasks: List[HiveTask]) -> Dict[str, Any]:
        """Build consensus from multiple agent analyses."""
        try:
            analyses = [task.output_data.get('analysis', '') for task in tasks if task.output_data]
            confidences = [task.output_data.get('confidence', 0.5) for task in tasks if task.output_data]

            # Simple consensus: combine analyses and average confidence
            combined_analysis = "\n\n".join([
                f"Agent Analysis {i+1}:\n{analysis}"
                for i, analysis in enumerate(analyses)
            ])

            average_confidence = sum(confidences) / len(confidences) if confidences else 0.5

            consensus = {
                'consensus_analysis': combined_analysis,
                'individual_analyses': analyses,
                'consensus_confidence': average_confidence,
                'participating_agents': len(tasks),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'consensus_method': 'weighted_average'
            }

            return consensus

        except Exception as e:
            logger.error(f"Failed to build consensus: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    async def _store_consensus_result(self, timeline_id: str, consensus: Dict[str, Any],
                                    tasks: List[HiveTask]):
        """Store consensus result in database."""
        try:
            if self.db:
                # Store as conversation record
                conversation_data = {
                    'messages': [
                        {
                            'role': 'system',
                            'content': f'Consensus analysis for timeline {timeline_id}',
                            'metadata': consensus
                        }
                    ]
                }

                # Get first agent ID for conversation association
                agent_id = tasks[0].assigned_node_id if tasks else list(self.agents.keys())[0]

                await self.db.store_conversation(
                    agent_id=agent_id,
                    messages=conversation_data['messages'],
                    title=f"Consensus Analysis - Timeline {timeline_id}"
                )

                # Store as metric
                await self.db.store_metric(
                    metric_name="hive_consensus_confidence",
                    metric_type="consensus",
                    value=consensus.get('consensus_confidence', 0.5),
                    source_component="hive_coordinator",
                    tags={
                        'timeline_id': timeline_id,
                        'participating_agents': consensus.get('participating_agents', 0)
                    }
                )

        except Exception as e:
            logger.error(f"Failed to store consensus result: {e}")

    async def get_swarm_status(self) -> Dict[str, Any]:
        """Get current status of the hive swarm."""
        try:
            db_health = await self.db.get_swarm_health() if self.db else {}

            return {
                'coordinator_status': 'running' if self.running else 'stopped',
                'total_agents': len(self.agents),
                'active_agents': len([a for a in self.agents.values() if a.status == 'active']),
                'pending_tasks': len(self.task_queue),
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'database_health': db_health,
                'consensus_threshold': self.consensus_threshold,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get swarm status: {e}")
            return {'error': str(e)}

    async def start(self):
        """Start the hive coordinator."""
        self.running = True
        console.print("[bold green]🐝 Hive Coordinator Started[/bold green]")

        # Start background tasks
        asyncio.create_task(self._heartbeat_monitor())
        asyncio.create_task(self._task_processor())

    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats."""
        while self.running:
            try:
                for agent in self.agents.values():
                    # Simple heartbeat - in real implementation, this would be network-based
                    if agent.status == "active":
                        # Update last heartbeat in database
                        if self.db:
                            await self.db.store_metric(
                                metric_name="agent_heartbeat",
                                metric_type="status",
                                value="active",
                                source_component=f"agent_{agent.name}",
                                tags={'agent_id': str(agent.agent_id)}
                            )

                await asyncio.sleep(30)  # Heartbeat every 30 seconds

            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")

    async def _task_processor(self):
        """Background task processor."""
        while self.running:
            try:
                if self.task_queue:
                    await self._process_task_queue()

                await asyncio.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Task processor error: {e}")

    async def stop(self):
        """Stop the hive coordinator."""
        self.running = False
        console.print("[red]Hive Coordinator Stopped[/red]")


# Global hive coordinator instance
_hive_coordinator: Optional[HiveCoordinator] = None

async def get_hive_coordinator(swarm_size: int = 3) -> HiveCoordinator:
    """Get the global hive coordinator instance."""
    global _hive_coordinator

    if _hive_coordinator is None:
        _hive_coordinator = HiveCoordinator(swarm_size=swarm_size)
        await _hive_coordinator.initialize()

    return _hive_coordinator

async def initialize_hive_system(swarm_size: int = 3) -> HiveCoordinator:
    """Initialize the AGI hive system."""
    coordinator = HiveCoordinator(swarm_size=swarm_size)
    await coordinator.initialize()
    await coordinator.start()
    return coordinator