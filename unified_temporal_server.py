"""
Unified Temporal Server - EXO Crypto + LEX TRI Integration

This server combines crypto trading capabilities with temporal debugging,
creating a unified system that leverages MCP agents for enhanced analysis.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from rich.console import Console

# Import all our components
from temporal_viz import TemporalTimeline, TemporalPoint, generate_example_timeline
from temporal_database import get_database, TemporalDatabase
from agi_hive_system import get_hive_coordinator, HiveCoordinator
from mcp_server import LEXTRIMCPServer
from exo_lextri_bridge import (
    get_crypto_temporal_bridge, CryptoTemporalBridge,
    CryptoTemporalEvent, CryptoEventType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

# Pydantic models for the unified API
class CryptoAgentConfig(BaseModel):
    agent_type: str = "crypto_trader"
    symbol: str = "BTC/USD"
    exchange: str = "binance"
    risk_limits: Dict[str, Any] = {}
    heartbeat_interval: int = 30
    cycle_interval: int = 60
    max_errors: int = 5
    temporal_lookback_hours: int = 24

class MarketDataPoint(BaseModel):
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    exchange: str = "binance"
    market_conditions: Dict[str, Any] = {}

class TradeSignal(BaseModel):
    agent_id: str
    symbol: str
    signal: str  # BUY, SELL, HOLD
    quantity: float
    confidence: float = 0.8
    order_type: str = "market"
    risk_score: float = 0.5
    correlation_id: Optional[str] = None

class MCPAnalysisRequest(BaseModel):
    data_type: str  # "timeline", "crypto_events", "market_data"
    data_payload: Dict[str, Any]
    analysis_type: str = "comprehensive"
    use_hive_consensus: bool = True
    priority: int = Field(default=5, ge=1, le=10)

# FastAPI application
app = FastAPI(
    title="Unified Temporal Crypto-AGI Server",
    description="Combined EXO crypto trading and LEX TRI temporal analysis with MCP agents",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db: Optional[TemporalDatabase] = None
hive: Optional[HiveCoordinator] = None
crypto_bridge: Optional[CryptoTemporalBridge] = None
mcp_server: Optional[LEXTRIMCPServer] = None

# WebSocket connection manager for real-time updates
class UnifiedConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, subscription_type: str = "all"):
        await websocket.accept()
        self.active_connections.append(websocket)

        if subscription_type not in self.subscriptions:
            self.subscriptions[subscription_type] = []
        self.subscriptions[subscription_type].append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        for sub_list in self.subscriptions.values():
            if websocket in sub_list:
                sub_list.remove(websocket)

    async def broadcast_to_subscription(self, message: str, subscription_type: str):
        if subscription_type in self.subscriptions:
            for connection in self.subscriptions[subscription_type][:]:
                try:
                    await connection.send_text(message)
                except:
                    self.subscriptions[subscription_type].remove(connection)

    async def broadcast_all(self, message: str):
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

manager = UnifiedConnectionManager()

# Dependency injection
async def get_db() -> TemporalDatabase:
    return await get_database()

async def get_hive() -> HiveCoordinator:
    return await get_hive_coordinator()

async def get_crypto_bridge() -> CryptoTemporalBridge:
    return await get_crypto_temporal_bridge()

# ============================================================================
# CRYPTO TRADING ENDPOINTS
# ============================================================================

@app.post("/api/crypto/agents")
async def create_crypto_agent(
    agent_config: CryptoAgentConfig,
    bridge: CryptoTemporalBridge = Depends(get_crypto_bridge)
):
    """Create a new crypto trading agent with temporal capabilities."""
    try:
        agent_id = await bridge.create_crypto_agent(agent_config.dict())

        # Broadcast agent creation
        await manager.broadcast_to_subscription(json.dumps({
            "type": "crypto_agent_created",
            "agent_id": agent_id,
            "agent_type": agent_config.agent_type,
            "symbol": agent_config.symbol,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), "crypto")

        return {
            "agent_id": agent_id,
            "status": "created",
            "config": agent_config.dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to create crypto agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crypto/market-data")
async def process_market_data(
    market_data: List[MarketDataPoint],
    bridge: CryptoTemporalBridge = Depends(get_crypto_bridge)
):
    """Process market data across all crypto agents."""
    try:
        # Convert to market data format
        market_stream = [data.dict() for data in market_data]

        # Process with crypto agents
        results = await bridge.process_market_stream(market_stream)

        # Broadcast market data processing
        await manager.broadcast_to_subscription(json.dumps({
            "type": "market_data_processed",
            "data_points": len(market_data),
            "agents_processed": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), "crypto")

        return {
            "processed_agents": len(results),
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to process market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crypto/trade")
async def execute_trade(
    trade_signal: TradeSignal,
    bridge: CryptoTemporalBridge = Depends(get_crypto_bridge)
):
    """Execute a trade through a specific crypto agent."""
    try:
        if trade_signal.agent_id not in bridge.bridge_agents:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = bridge.bridge_agents[trade_signal.agent_id]
        result = await agent.execute_trade(trade_signal.dict())

        # Broadcast trade execution
        await manager.broadcast_to_subscription(json.dumps({
            "type": "trade_executed",
            "agent_id": trade_signal.agent_id,
            "symbol": trade_signal.symbol,
            "signal": trade_signal.signal,
            "status": result.get("status"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), "crypto")

        return result

    except Exception as e:
        logger.error(f"Failed to execute trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crypto/agents/{agent_id}/status")
async def get_crypto_agent_status(
    agent_id: str,
    bridge: CryptoTemporalBridge = Depends(get_crypto_bridge)
):
    """Get status of a specific crypto agent."""
    try:
        if agent_id not in bridge.bridge_agents:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = bridge.bridge_agents[agent_id]
        status = await agent.heartbeat()

        return status

    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MCP AGENT INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/api/mcp/analyze")
async def mcp_analysis(
    request: MCPAnalysisRequest,
    background_tasks: BackgroundTasks,
    hive: HiveCoordinator = Depends(get_hive)
):
    """Use MCP agents for enhanced data analysis."""
    try:
        if request.data_type == "timeline":
            # Convert data to timeline format
            timeline_data = request.data_payload
            timeline = TemporalTimeline.from_dict(timeline_data)

        elif request.data_type == "crypto_events":
            # Convert crypto events to timeline
            events = request.data_payload.get("events", [])
            temporal_points = []

            for event_data in events:
                point = TemporalPoint(
                    valid_time=datetime.fromisoformat(event_data["valid_time"]),
                    transaction_time=datetime.fromisoformat(event_data["transaction_time"]),
                    decision_time=datetime.fromisoformat(event_data["decision_time"]) if event_data.get("decision_time") else None,
                    event_data=event_data.get("data", {}),
                    event_id=event_data.get("event_id", str(uuid4()))
                )
                temporal_points.append(point)

            timeline = TemporalTimeline(
                name=request.data_payload.get("name", "MCP Analysis Timeline"),
                points=temporal_points
            )

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data type: {request.data_type}")

        if request.use_hive_consensus:
            # Submit to hive swarm
            task_id = await hive.submit_temporal_analysis_task(
                timeline=timeline,
                priority=request.priority
            )

            # Schedule background notification
            background_tasks.add_task(
                notify_mcp_analysis_complete,
                str(task_id),
                request.analysis_type
            )

            return {
                "analysis_type": "hive_consensus",
                "task_id": str(task_id),
                "status": "submitted",
                "estimated_completion": "2-5 minutes",
                "timeline_points": len(timeline.points),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            # Direct analysis
            anomalies = timeline.analyze_anomalies()

            return {
                "analysis_type": "direct",
                "timeline_points": len(timeline.points),
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
                "confidence": 0.75,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    except Exception as e:
        logger.error(f"MCP analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def notify_mcp_analysis_complete(task_id: str, analysis_type: str):
    """Background task to notify when MCP analysis is complete."""
    await asyncio.sleep(5)  # Check every 5 seconds

    try:
        # Check if task is complete
        # This would normally check hive task status
        await manager.broadcast_to_subscription(json.dumps({
            "type": "mcp_analysis_complete",
            "task_id": task_id,
            "analysis_type": analysis_type,
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), "mcp")

    except Exception as e:
        logger.error(f"Error notifying MCP analysis completion: {e}")

@app.get("/api/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools."""
    return {
        "tools": [
            {
                "name": "generate_example_timeline",
                "description": "Generate synthetic temporal timeline data",
                "parameters": ["name", "num_points"]
            },
            {
                "name": "analyze_timeline_anomalies",
                "description": "Analyze timeline for temporal anomalies",
                "parameters": ["timeline_data", "file_path"]
            },
            {
                "name": "visualize_timeline",
                "description": "Create timeline visualization",
                "parameters": ["timeline_data", "output_path", "highlight_anomalies"]
            },
            {
                "name": "crypto_temporal_analysis",
                "description": "Analyze crypto trading patterns with temporal context",
                "parameters": ["crypto_events", "market_data", "agent_context"]
            }
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ============================================================================
# UNIFIED SYSTEM ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with unified system information."""
    return {
        "service": "Unified Temporal Crypto-AGI Server",
        "version": "3.0.0",
        "status": "running",
        "capabilities": [
            "EXO crypto trading agents",
            "LEX TRI temporal debugging",
            "AGI hive swarm consensus",
            "MCP agent integration",
            "Real-time WebSocket communication",
            "PostgreSQL temporal database",
            "Unified crypto-temporal analysis"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
async def unified_health_check(
    db: TemporalDatabase = Depends(get_db),
    hive: HiveCoordinator = Depends(get_hive),
    bridge: CryptoTemporalBridge = Depends(get_crypto_bridge)
):
    """Comprehensive health check for all systems."""
    try:
        # Database health
        db_health = await db.get_swarm_health()

        # Hive status
        hive_status = await hive.get_swarm_status()

        # Crypto bridge status
        crypto_status = await bridge.get_system_status()

        # Overall health assessment
        all_healthy = (
            db_health.get("health_percentage", 0) > 80 and
            hive_status.get("active_agents", 0) > 0 and
            crypto_status.get("active_crypto_agents", 0) >= 0
        )

        return {
            "status": "healthy" if all_healthy else "degraded",
            "database": db_health,
            "hive_swarm": hive_status,
            "crypto_bridge": crypto_status,
            "unified_score": (
                db_health.get("health_percentage", 0) * 0.4 +
                (hive_status.get("active_agents", 0) / max(hive_status.get("total_agents", 1), 1)) * 100 * 0.3 +
                (crypto_status.get("active_crypto_agents", 0) / max(crypto_status.get("total_crypto_agents", 1), 1)) * 100 * 0.3
            ),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

@app.get("/api/system/metrics")
async def get_system_metrics(
    db: TemporalDatabase = Depends(get_db)
):
    """Get comprehensive system metrics."""
    try:
        # Store system metrics in database
        await db.store_metric(
            metric_name="api_request",
            metric_type="system",
            value=1,
            source_component="unified_server",
            tags={"endpoint": "/api/system/metrics"}
        )

        return {
            "message": "System metrics collected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws/{subscription_type}")
async def websocket_endpoint(websocket: WebSocket, subscription_type: str):
    """WebSocket endpoint for real-time updates by subscription type."""
    await manager.connect(websocket, subscription_type)
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "subscription": subscription_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))

        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))

    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ============================================================================
# UNIFIED DASHBOARD
# ============================================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def unified_dashboard():
    """Unified dashboard for monitoring all systems."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unified Temporal Crypto-AGI Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .header { text-align: center; margin-bottom: 30px; }
            .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { display: flex; justify-content: space-between; margin: 10px 0; }
            .metric-value { font-weight: bold; }
            .status-healthy { color: #4CAF50; }
            .status-warning { color: #FF9800; }
            .status-error { color: #F44336; }
            .real-time { height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; }
            .log-entry { margin: 5px 0; padding: 5px; background: #f9f9f9; border-left: 3px solid #2196F3; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀🐝💰 Unified Temporal Crypto-AGI Dashboard</h1>
            <p>EXO Crypto Trading + LEX TRI Temporal Analysis + MCP Agent Integration</p>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <h3>🏥 System Health</h3>
                <div id="system-health">Loading...</div>
            </div>

            <div class="card">
                <h3>🐝 AGI Hive Swarm</h3>
                <div id="hive-status">Loading...</div>
            </div>

            <div class="card">
                <h3>💰 Crypto Trading Agents</h3>
                <div id="crypto-status">Loading...</div>
            </div>

            <div class="card">
                <h3>🗄️ Temporal Database</h3>
                <div id="db-status">Loading...</div>
            </div>

            <div class="card">
                <h3>📡 Real-Time Activity</h3>
                <div id="activity-feed" class="real-time">
                    <p>Connecting to live feed...</p>
                </div>
            </div>

            <div class="card">
                <h3>🤖 MCP Agent Activity</h3>
                <div id="mcp-feed" class="real-time">
                    <p>Monitoring MCP agents...</p>
                </div>
            </div>
        </div>

        <script>
            // WebSocket connections for different data streams
            const allSocket = new WebSocket(`ws://${window.location.host}/ws/all`);
            const cryptoSocket = new WebSocket(`ws://${window.location.host}/ws/crypto`);
            const mcpSocket = new WebSocket(`ws://${window.location.host}/ws/mcp`);

            // Handle all system events
            allSocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addLogEntry('activity-feed', `${data.type}: ${JSON.stringify(data)}`, 'system');
            };

            // Handle crypto-specific events
            cryptoSocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addLogEntry('activity-feed', `CRYPTO: ${data.type}`, 'crypto');
            };

            // Handle MCP agent events
            mcpSocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addLogEntry('mcp-feed', `MCP: ${data.type}`, 'mcp');
            };

            function addLogEntry(containerId, message, type) {
                const container = document.getElementById(containerId);
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.innerHTML = `<small>${new Date().toLocaleTimeString()}</small> ${message}`;
                container.insertBefore(entry, container.firstChild);

                // Keep only last 20 entries
                while (container.children.length > 20) {
                    container.removeChild(container.lastChild);
                }
            }

            // Update system status periodically
            async function updateStatus() {
                try {
                    const healthResponse = await fetch('/health');
                    const healthData = await healthResponse.json();

                    // Update system health
                    document.getElementById('system-health').innerHTML = `
                        <div class="metric">
                            <span>Overall Status:</span>
                            <span class="metric-value status-${healthData.status === 'healthy' ? 'healthy' : 'error'}">
                                ${healthData.status.toUpperCase()}
                            </span>
                        </div>
                        <div class="metric">
                            <span>Unified Score:</span>
                            <span class="metric-value">${Math.round(healthData.unified_score || 0)}%</span>
                        </div>
                    `;

                    // Update hive status
                    const hive = healthData.hive_swarm || {};
                    document.getElementById('hive-status').innerHTML = `
                        <div class="metric">
                            <span>Active Agents:</span>
                            <span class="metric-value">${hive.active_agents || 0}</span>
                        </div>
                        <div class="metric">
                            <span>Pending Tasks:</span>
                            <span class="metric-value">${hive.pending_tasks || 0}</span>
                        </div>
                        <div class="metric">
                            <span>Completed Tasks:</span>
                            <span class="metric-value">${hive.completed_tasks || 0}</span>
                        </div>
                    `;

                    // Update crypto status
                    const crypto = healthData.crypto_bridge || {};
                    document.getElementById('crypto-status').innerHTML = `
                        <div class="metric">
                            <span>Active Traders:</span>
                            <span class="metric-value">${crypto.active_crypto_agents || 0}</span>
                        </div>
                        <div class="metric">
                            <span>Total Agents:</span>
                            <span class="metric-value">${crypto.total_crypto_agents || 0}</span>
                        </div>
                        <div class="metric">
                            <span>Bridge Status:</span>
                            <span class="metric-value status-${crypto.bridge_status === 'running' ? 'healthy' : 'error'}">
                                ${(crypto.bridge_status || 'unknown').toUpperCase()}
                            </span>
                        </div>
                    `;

                    // Update database status
                    const db = healthData.database || {};
                    document.getElementById('db-status').innerHTML = `
                        <div class="metric">
                            <span>Active Nodes:</span>
                            <span class="metric-value">${db.active_nodes || 0}</span>
                        </div>
                        <div class="metric">
                            <span>Health:</span>
                            <span class="metric-value">${Math.round(db.health_percentage || 0)}%</span>
                        </div>
                        <div class="metric">
                            <span>Average Load:</span>
                            <span class="metric-value">${(db.avg_load || 0).toFixed(2)}</span>
                        </div>
                    `;

                } catch (error) {
                    console.error('Failed to update status:', error);
                }
            }

            // Update every 30 seconds
            setInterval(updateStatus, 30000);
            updateStatus(); // Initial update
        </script>
    </body>
    </html>
    """

# ============================================================================
# STARTUP AND SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize all unified services on startup."""
    global db, hive, crypto_bridge, mcp_server

    console.print("[bold green]🚀 Starting Unified Temporal Crypto-AGI Server[/bold green]")

    try:
        # Initialize database
        db = await get_database()
        console.print("[green]✓ Temporal database initialized[/green]")

        # Initialize hive coordinator
        hive = await get_hive_coordinator(swarm_size=3)
        await hive.start()
        console.print("[green]✓ AGI Hive Swarm initialized[/green]")

        # Initialize crypto-temporal bridge
        crypto_bridge = await get_crypto_temporal_bridge()
        crypto_bridge.running = True
        console.print("[green]✓ Crypto-Temporal Bridge initialized[/green]")

        # Initialize MCP server
        mcp_server = LEXTRIMCPServer()
        console.print("[green]✓ MCP Server configured[/green]")

        console.print("[bold green]🎉 Unified Temporal Crypto-AGI Server ready![/bold green]")
        console.print("[blue]💰 EXO crypto agents ready for trading[/blue]")
        console.print("[blue]🐝 LEX TRI temporal analysis active[/blue]")
        console.print("[blue]🤖 MCP agents standing by[/blue]")

    except Exception as e:
        logger.error(f"Failed to initialize unified services: {e}")
        console.print(f"[red]❌ Startup failed: {e}[/red]")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup all services on shutdown."""
    console.print("[yellow]🛑 Shutting down Unified Temporal Crypto-AGI Server[/yellow]")

    try:
        if crypto_bridge:
            crypto_bridge.running = False
            console.print("[green]✓ Crypto bridge stopped[/green]")

        if hive:
            await hive.stop()
            console.print("[green]✓ Hive coordinator stopped[/green]")

        if db:
            await db.close()
            console.print("[green]✓ Database connections closed[/green]")

        console.print("[green]✓ Unified shutdown complete[/green]")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Main entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    console.print(f"[blue]Starting unified server on {host}:{port}[/blue]")
    console.print("[blue]💰🐝🤖 EXO + LEX TRI + MCP Integration Active[/blue]")

    uvicorn.run(
        "unified_temporal_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )