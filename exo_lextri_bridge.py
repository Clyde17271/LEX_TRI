"""
EXO-LEX TRI Bridge System

This module creates a unified bridge between the EXO crypto agent swarm
and LEX TRI temporal system, enabling crypto agents to leverage tri-temporal
debugging while maintaining their trading capabilities.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4
from dataclasses import dataclass, asdict
from enum import Enum

# Import EXO components (simulated - adjust imports based on actual EXO structure)
from temporal_viz import TemporalPoint, TemporalTimeline
from temporal_database import get_database, TemporalDatabase
from agi_hive_system import get_hive_coordinator, HiveCoordinator, AGIAgent
from mcp_server import LEXTRIMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoEventType(Enum):
    """Crypto-specific event types for temporal tracking."""
    MARKET_OBSERVATION = "market_observation"
    TRADE_SIGNAL = "trade_signal"
    TRADE_EXECUTION = "trade_execution"
    PRICE_UPDATE = "price_update"
    AGENT_DECISION = "agent_decision"
    RISK_ASSESSMENT = "risk_assessment"
    WHALE_MOVEMENT = "whale_movement"
    NEWS_EVENT = "news_event"
    SENTIMENT_SHIFT = "sentiment_shift"
    PREDICTION = "prediction"
    VALIDATION_RESULT = "validation_result"
    ANOMALY_DETECTED = "anomaly_detected"
    PORTFOLIO_UPDATE = "portfolio_update"
    ORDER_BOOK_CHANGE = "order_book_change"
    ARBITRAGE_OPPORTUNITY = "arbitrage_opportunity"

@dataclass
class CryptoTemporalEvent:
    """
    Crypto-specific temporal event that bridges EXO and LEX TRI systems.
    Combines crypto trading data with tri-temporal debugging capabilities.
    """
    event_id: str
    event_type: CryptoEventType
    agent_id: str

    # Tri-temporal dimensions
    valid_time: datetime      # When the market event actually occurred
    transaction_time: datetime # When our system observed/recorded it
    decision_time: Optional[datetime] = None  # When trading decision was made

    # Crypto-specific data
    symbol: Optional[str] = None
    price: Optional[float] = None
    volume: Optional[float] = None
    exchange: Optional[str] = None

    # Trading context
    portfolio_state: Optional[Dict[str, Any]] = None
    risk_metrics: Optional[Dict[str, Any]] = None
    market_conditions: Optional[Dict[str, Any]] = None

    # Event metadata
    data: Dict[str, Any] = None
    confidence: float = 1.0
    certainty: float = 1.0

    # Causality and correlation
    caused_by: List[str] = None
    correlation_id: Optional[str] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.caused_by is None:
            self.caused_by = []

    def to_temporal_point(self) -> TemporalPoint:
        """Convert to LEX TRI TemporalPoint for temporal analysis."""
        event_data = {
            'crypto_event': True,
            'event_type': self.event_type.value,
            'symbol': self.symbol,
            'price': self.price,
            'volume': self.volume,
            'exchange': self.exchange,
            'portfolio_state': self.portfolio_state,
            'risk_metrics': self.risk_metrics,
            'market_conditions': self.market_conditions,
            'confidence': self.confidence,
            'certainty': self.certainty,
            'correlation_id': self.correlation_id,
            **self.data
        }

        return TemporalPoint(
            valid_time=self.valid_time,
            transaction_time=self.transaction_time,
            decision_time=self.decision_time,
            event_data=event_data,
            event_id=self.event_id
        )

class EXOAgentBridge:
    """
    Bridge that adapts EXO crypto agents to work with LEX TRI temporal system.
    Maintains EXO agent lifecycle while adding temporal debugging capabilities.
    """

    def __init__(self, exo_agent_config: Dict[str, Any],
                 temporal_db: TemporalDatabase,
                 hive_coordinator: HiveCoordinator):
        self.agent_id = exo_agent_config.get('agent_id', str(uuid4()))
        self.agent_type = exo_agent_config.get('agent_type', 'crypto_trader')
        self.config = exo_agent_config
        self.temporal_db = temporal_db
        self.hive = hive_coordinator

        # EXO-style state tracking
        self.state = "created"
        self.created_at = datetime.now(timezone.utc)
        self.last_heartbeat = self.created_at
        self.error_count = 0
        self.max_errors = exo_agent_config.get("max_errors", 5)

        # Crypto-specific state
        self.portfolio = {}
        self.active_positions = {}
        self.recent_signals = []
        self.risk_limits = exo_agent_config.get('risk_limits', {})

        # Temporal memory for AGI reasoning
        self.temporal_events: List[CryptoTemporalEvent] = []
        self.temporal_timeline_id: Optional[UUID] = None

        logger.info(f"Created EXO-LEX TRI bridge agent: {self.agent_id}")

    async def initialize(self) -> bool:
        """Initialize the bridged agent with both EXO and LEX TRI capabilities."""
        try:
            self.state = "initializing"

            # Register with LEX TRI temporal database
            await self.temporal_db.register_agi_agent(
                name=f"EXO-{self.agent_type}-{self.agent_id[:8]}",
                agent_type=f"crypto_{self.agent_type}",
                capabilities=[
                    "crypto_trading",
                    "temporal_analysis",
                    "risk_management",
                    "market_observation",
                    "portfolio_management"
                ],
                config=self.config
            )

            # Create temporal timeline for this agent
            initial_timeline = TemporalTimeline(
                name=f"Crypto Agent {self.agent_id} Timeline",
                points=[]
            )
            initial_timeline.description = f"Trading timeline for {self.agent_type} agent"

            self.temporal_timeline_id = await self.temporal_db.store_timeline(initial_timeline)

            # Record initialization event
            init_event = CryptoTemporalEvent(
                event_id=str(uuid4()),
                event_type=CryptoEventType.AGENT_DECISION,
                agent_id=self.agent_id,
                valid_time=self.created_at,
                transaction_time=datetime.now(timezone.utc),
                data={
                    'action': 'agent_initialized',
                    'agent_type': self.agent_type,
                    'capabilities': ['crypto_trading', 'temporal_analysis']
                }
            )

            await self._record_temporal_event(init_event)

            self.state = "active"
            logger.info(f"EXO-LEX TRI bridge agent {self.agent_id} initialized successfully")
            return True

        except Exception as e:
            self.state = "error"
            self.error_count += 1
            logger.error(f"Failed to initialize bridge agent {self.agent_id}: {e}")
            return False

    async def process_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process market data with temporal tracking."""
        try:
            # Create temporal event for market observation
            market_event = CryptoTemporalEvent(
                event_id=str(uuid4()),
                event_type=CryptoEventType.MARKET_OBSERVATION,
                agent_id=self.agent_id,
                valid_time=market_data.get('timestamp', datetime.now(timezone.utc)),
                transaction_time=datetime.now(timezone.utc),
                symbol=market_data.get('symbol'),
                price=market_data.get('price'),
                volume=market_data.get('volume'),
                exchange=market_data.get('exchange'),
                market_conditions=market_data.get('market_conditions', {}),
                data=market_data
            )

            # Record in temporal database
            await self._record_temporal_event(market_event)

            # Analyze for trading signals using temporal context
            signal_analysis = await self._analyze_trading_signals(market_event)

            return signal_analysis

        except Exception as e:
            logger.error(f"Error processing market data in agent {self.agent_id}: {e}")
            self.error_count += 1
            return {'error': str(e)}

    async def _analyze_trading_signals(self, market_event: CryptoTemporalEvent) -> Dict[str, Any]:
        """Analyze trading signals using temporal pattern recognition."""
        try:
            # Get temporal context from recent events
            recent_events = await self._get_recent_temporal_context(hours=24)

            # Use MCP agents for enhanced analysis
            timeline_data = {
                'current_event': asdict(market_event),
                'recent_context': [asdict(event) for event in recent_events],
                'agent_id': self.agent_id,
                'analysis_type': 'trading_signal'
            }

            # Submit to hive swarm for consensus analysis
            hive_task_id = await self.hive.submit_temporal_analysis_task(
                timeline=self._build_trading_timeline(recent_events + [market_event]),
                priority=7  # High priority for trading decisions
            )

            # For immediate response, also do local analysis
            local_signals = self._local_signal_analysis(market_event, recent_events)

            return {
                'local_analysis': local_signals,
                'hive_task_id': str(hive_task_id),
                'temporal_context_size': len(recent_events),
                'confidence': 0.8,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing trading signals: {e}")
            return {'error': str(e), 'confidence': 0.0}

    def _local_signal_analysis(self, current_event: CryptoTemporalEvent,
                              context_events: List[CryptoTemporalEvent]) -> Dict[str, Any]:
        """Perform local signal analysis using temporal patterns."""

        # Simple trend analysis based on temporal sequence
        price_events = [e for e in context_events
                       if e.event_type == CryptoEventType.PRICE_UPDATE and e.price is not None]

        if len(price_events) < 3:
            return {'signal': 'HOLD', 'reason': 'insufficient_data', 'strength': 0.1}

        # Calculate temporal price momentum
        recent_prices = [e.price for e in price_events[-5:]]
        price_trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] if recent_prices[0] != 0 else 0

        # Temporal lag analysis
        avg_latency = sum(e.transaction_time.timestamp() - e.valid_time.timestamp()
                         for e in price_events) / len(price_events)

        # Generate signal based on temporal analysis
        if price_trend > 0.02 and avg_latency < 5:  # Strong uptrend with low latency
            signal = 'BUY'
            strength = min(0.8, price_trend * 10)
        elif price_trend < -0.02 and avg_latency < 5:  # Strong downtrend with low latency
            signal = 'SELL'
            strength = min(0.8, abs(price_trend) * 10)
        else:
            signal = 'HOLD'
            strength = 0.3

        return {
            'signal': signal,
            'strength': strength,
            'price_trend': price_trend,
            'avg_latency': avg_latency,
            'reason': 'temporal_momentum_analysis'
        }

    async def execute_trade(self, trade_signal: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade with temporal tracking and risk management."""
        try:
            # Create trade execution event
            trade_event = CryptoTemporalEvent(
                event_id=str(uuid4()),
                event_type=CryptoEventType.TRADE_EXECUTION,
                agent_id=self.agent_id,
                valid_time=datetime.now(timezone.utc),
                transaction_time=datetime.now(timezone.utc),
                decision_time=datetime.now(timezone.utc),
                symbol=trade_signal.get('symbol'),
                data={
                    'signal': trade_signal.get('signal'),
                    'quantity': trade_signal.get('quantity'),
                    'order_type': trade_signal.get('order_type', 'market'),
                    'risk_score': trade_signal.get('risk_score', 0.5)
                },
                correlation_id=trade_signal.get('correlation_id')
            )

            # Risk check before execution
            risk_assessment = await self._assess_trade_risk(trade_event)

            if risk_assessment['approved']:
                # Record successful trade execution
                trade_event.data['execution_status'] = 'executed'
                trade_event.data['risk_assessment'] = risk_assessment

                # Update portfolio state
                await self._update_portfolio(trade_event)

                execution_result = {
                    'status': 'executed',
                    'trade_id': trade_event.event_id,
                    'timestamp': trade_event.transaction_time.isoformat(),
                    'risk_assessment': risk_assessment
                }
            else:
                # Record rejected trade
                trade_event.data['execution_status'] = 'rejected'
                trade_event.data['rejection_reason'] = risk_assessment['reason']

                execution_result = {
                    'status': 'rejected',
                    'reason': risk_assessment['reason'],
                    'risk_assessment': risk_assessment
                }

            # Always record the event for temporal analysis
            await self._record_temporal_event(trade_event)

            return execution_result

        except Exception as e:
            logger.error(f"Error executing trade in agent {self.agent_id}: {e}")
            return {'status': 'error', 'error': str(e)}

    async def _assess_trade_risk(self, trade_event: CryptoTemporalEvent) -> Dict[str, Any]:
        """Assess trade risk using temporal patterns and current state."""
        try:
            # Get recent trading history
            recent_trades = await self._get_recent_trades(hours=24)

            # Calculate risk metrics
            daily_volume = sum(float(trade.data.get('quantity', 0)) for trade in recent_trades)
            max_daily_volume = self.risk_limits.get('max_daily_volume', 10000)

            current_quantity = float(trade_event.data.get('quantity', 0))
            volume_risk = (daily_volume + current_quantity) / max_daily_volume

            # Temporal risk analysis
            recent_losses = [trade for trade in recent_trades
                           if trade.data.get('pnl', 0) < 0]
            loss_streak = len(recent_losses)
            max_loss_streak = self.risk_limits.get('max_loss_streak', 3)

            # Overall risk score
            risk_score = max(volume_risk, loss_streak / max_loss_streak)

            approved = risk_score < 0.8

            return {
                'approved': approved,
                'risk_score': risk_score,
                'volume_risk': volume_risk,
                'loss_streak': loss_streak,
                'reason': 'acceptable_risk' if approved else 'risk_threshold_exceeded'
            }

        except Exception as e:
            logger.error(f"Error assessing trade risk: {e}")
            return {
                'approved': False,
                'risk_score': 1.0,
                'reason': f'risk_assessment_error: {str(e)}'
            }

    async def _record_temporal_event(self, event: CryptoTemporalEvent):
        """Record temporal event in both local memory and database."""
        try:
            # Add to local temporal memory
            self.temporal_events.append(event)

            # Convert to TemporalPoint and store in database
            temporal_point = event.to_temporal_point()

            await self.temporal_db.store_temporal_event(
                temporal_point=temporal_point,
                timeline_id=self.temporal_timeline_id,
                event_type=event.event_type.value,
                event_source="exo_crypto_agent"
            )

            # Keep local memory bounded
            if len(self.temporal_events) > 1000:
                self.temporal_events = self.temporal_events[-800:]  # Keep last 800 events

        except Exception as e:
            logger.error(f"Error recording temporal event: {e}")

    async def _get_recent_temporal_context(self, hours: int = 24) -> List[CryptoTemporalEvent]:
        """Get recent temporal events for context analysis."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        return [event for event in self.temporal_events
                if event.transaction_time >= cutoff_time]

    async def _get_recent_trades(self, hours: int = 24) -> List[CryptoTemporalEvent]:
        """Get recent trade executions for risk analysis."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        return [event for event in self.temporal_events
                if (event.event_type == CryptoEventType.TRADE_EXECUTION and
                    event.transaction_time >= cutoff_time)]

    def _build_trading_timeline(self, events: List[CryptoTemporalEvent]) -> TemporalTimeline:
        """Build a TemporalTimeline from crypto events for hive analysis."""
        temporal_points = [event.to_temporal_point() for event in events]

        timeline = TemporalTimeline(
            name=f"Trading Timeline - Agent {self.agent_id[:8]}",
            points=temporal_points
        )

        timeline.description = f"Crypto trading timeline for temporal analysis"
        return timeline

    async def _update_portfolio(self, trade_event: CryptoTemporalEvent):
        """Update portfolio state based on trade execution."""
        try:
            symbol = trade_event.symbol
            quantity = float(trade_event.data.get('quantity', 0))
            signal = trade_event.data.get('signal')

            if symbol not in self.portfolio:
                self.portfolio[symbol] = 0

            if signal == 'BUY':
                self.portfolio[symbol] += quantity
            elif signal == 'SELL':
                self.portfolio[symbol] -= quantity

            # Record portfolio update event
            portfolio_event = CryptoTemporalEvent(
                event_id=str(uuid4()),
                event_type=CryptoEventType.PORTFOLIO_UPDATE,
                agent_id=self.agent_id,
                valid_time=trade_event.decision_time or datetime.now(timezone.utc),
                transaction_time=datetime.now(timezone.utc),
                symbol=symbol,
                data={
                    'portfolio_state': dict(self.portfolio),
                    'change': quantity if signal == 'BUY' else -quantity,
                    'trigger_trade_id': trade_event.event_id
                },
                caused_by=[trade_event.event_id]
            )

            await self._record_temporal_event(portfolio_event)

        except Exception as e:
            logger.error(f"Error updating portfolio: {e}")

    async def get_temporal_health_metrics(self) -> Dict[str, Any]:
        """Get temporal-specific health metrics for monitoring."""
        try:
            recent_events = await self._get_recent_temporal_context(hours=1)

            # Calculate temporal metrics
            if recent_events:
                avg_latency = sum(e.transaction_time.timestamp() - e.valid_time.timestamp()
                                for e in recent_events) / len(recent_events)

                decision_events = [e for e in recent_events if e.decision_time]
                avg_decision_delay = (sum(e.decision_time.timestamp() - e.transaction_time.timestamp()
                                        for e in decision_events) / len(decision_events)) if decision_events else 0
            else:
                avg_latency = 0
                avg_decision_delay = 0

            return {
                'total_events': len(self.temporal_events),
                'recent_events_1h': len(recent_events),
                'avg_latency_seconds': avg_latency,
                'avg_decision_delay_seconds': avg_decision_delay,
                'portfolio_positions': len([k for k, v in self.portfolio.items() if v != 0]),
                'timeline_id': str(self.temporal_timeline_id) if self.temporal_timeline_id else None,
                'temporal_health': 'healthy' if avg_latency < 10 and avg_decision_delay < 30 else 'degraded'
            }

        except Exception as e:
            logger.error(f"Error getting temporal health metrics: {e}")
            return {'error': str(e)}

    async def heartbeat(self) -> Dict[str, Any]:
        """Enhanced heartbeat with temporal metrics."""
        self.last_heartbeat = datetime.now(timezone.utc)

        # Get temporal health metrics
        temporal_metrics = await self.get_temporal_health_metrics()

        return {
            'agent_id': self.agent_id,
            'agent_type': f"exo_crypto_{self.agent_type}",
            'state': self.state,
            'timestamp': self.last_heartbeat.isoformat(),
            'uptime_seconds': (self.last_heartbeat - self.created_at).total_seconds(),
            'error_count': self.error_count,
            'portfolio_value': sum(abs(v) for v in self.portfolio.values()),
            'temporal_metrics': temporal_metrics,
            'is_healthy': (self.error_count < self.max_errors and
                          self.state == "active" and
                          temporal_metrics.get('temporal_health') == 'healthy')
        }


class CryptoTemporalBridge:
    """
    Main bridge coordinator that manages multiple EXO crypto agents
    with LEX TRI temporal capabilities and MCP integration.
    """

    def __init__(self):
        self.bridge_agents: Dict[str, EXOAgentBridge] = {}
        self.temporal_db: Optional[TemporalDatabase] = None
        self.hive: Optional[HiveCoordinator] = None
        self.mcp_server: Optional[LEXTRIMCPServer] = None
        self.running = False

    async def initialize(self):
        """Initialize the crypto-temporal bridge system."""
        try:
            # Get database and hive connections
            self.temporal_db = await get_database()
            self.hive = await get_hive_coordinator()

            # Initialize MCP server
            self.mcp_server = LEXTRIMCPServer()

            logger.info("Crypto-Temporal Bridge initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize crypto-temporal bridge: {e}")
            raise

    async def create_crypto_agent(self, agent_config: Dict[str, Any]) -> str:
        """Create a new crypto agent with temporal capabilities."""
        try:
            bridge_agent = EXOAgentBridge(
                exo_agent_config=agent_config,
                temporal_db=self.temporal_db,
                hive_coordinator=self.hive
            )

            success = await bridge_agent.initialize()
            if success:
                self.bridge_agents[bridge_agent.agent_id] = bridge_agent
                logger.info(f"Created crypto-temporal agent: {bridge_agent.agent_id}")
                return bridge_agent.agent_id
            else:
                raise Exception("Failed to initialize bridge agent")

        except Exception as e:
            logger.error(f"Error creating crypto agent: {e}")
            raise

    async def process_market_stream(self, market_data_stream: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a stream of market data across all crypto agents."""
        results = {}

        for agent_id, agent in self.bridge_agents.items():
            if agent.state == "active":
                agent_results = []

                for market_data in market_data_stream:
                    try:
                        result = await agent.process_market_data(market_data)
                        agent_results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing market data for agent {agent_id}: {e}")
                        agent_results.append({'error': str(e)})

                results[agent_id] = agent_results

        return results

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the crypto-temporal bridge system."""
        try:
            # Get agent statuses
            agent_statuses = {}
            for agent_id, agent in self.bridge_agents.items():
                agent_statuses[agent_id] = await agent.heartbeat()

            # Get hive status
            hive_status = await self.hive.get_swarm_status() if self.hive else {}

            # Get database health
            db_health = await self.temporal_db.get_swarm_health() if self.temporal_db else {}

            return {
                'bridge_status': 'running' if self.running else 'stopped',
                'total_crypto_agents': len(self.bridge_agents),
                'active_crypto_agents': len([a for a in self.bridge_agents.values() if a.state == "active"]),
                'agent_statuses': agent_statuses,
                'hive_swarm_status': hive_status,
                'database_health': db_health,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}


# Global bridge instance
_crypto_temporal_bridge: Optional[CryptoTemporalBridge] = None

async def get_crypto_temporal_bridge() -> CryptoTemporalBridge:
    """Get the global crypto-temporal bridge instance."""
    global _crypto_temporal_bridge

    if _crypto_temporal_bridge is None:
        _crypto_temporal_bridge = CryptoTemporalBridge()
        await _crypto_temporal_bridge.initialize()

    return _crypto_temporal_bridge

async def initialize_crypto_temporal_bridge() -> CryptoTemporalBridge:
    """Initialize the crypto-temporal bridge system."""
    bridge = CryptoTemporalBridge()
    await bridge.initialize()
    return bridge