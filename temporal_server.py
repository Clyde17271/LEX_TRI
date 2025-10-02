"""
Temporal Server for LEX TRI AGI Hive System

This is the main server that integrates all components:
- PostgreSQL temporal database
- AGI hive swarm coordination
- MCP server for AI client integration
- FastAPI web interface
- WebSocket real-time communication
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from rich.console import Console

# Import our components
from temporal_viz import TemporalTimeline, TemporalPoint, generate_example_timeline
from temporal_database import get_database, TemporalDatabase
from agi_hive_system import get_hive_coordinator, HiveCoordinator
from mcp_server import LEXTRIMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

# Pydantic models for API
class TemporalEventCreate(BaseModel):
    valid_time: datetime
    transaction_time: datetime
    decision_time: Optional[datetime] = None
    event_type: str = "api_event"
    event_source: str = "temporal_server"
    event_data: Dict[str, Any] = {}

class TimelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    points: List[TemporalEventCreate]

class AnalysisRequest(BaseModel):
    timeline_id: Optional[str] = None
    timeline_data: Optional[Dict[str, Any]] = None
    use_hive_consensus: bool = True
    priority: int = Field(default=5, ge=1, le=10)

class HiveTaskStatus(BaseModel):
    task_id: str
    status: str
    progress_percentage: int
    result: Optional[Dict[str, Any]] = None

# FastAPI application
app = FastAPI(
    title="LEX TRI Temporal AGI Server",
    description="Temporal debugging and analysis with AGI hive swarm capabilities",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db: Optional[TemporalDatabase] = None
hive: Optional[HiveCoordinator] = None
mcp_server: Optional[LEXTRIMCPServer] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Dependency injection
async def get_db() -> TemporalDatabase:
    return await get_database()

async def get_hive() -> HiveCoordinator:
    return await get_hive_coordinator()

# API Routes

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "service": "LEX TRI Temporal AGI Server",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Tri-temporal data management",
            "AGI hive swarm analysis",
            "MCP server integration",
            "Real-time WebSocket communication",
            "PostgreSQL with vector extensions"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
async def health_check(db: TemporalDatabase = Depends(get_db),
                      hive: HiveCoordinator = Depends(get_hive)):
    """Comprehensive health check."""
    try:
        # Check database health
        db_health = await db.get_swarm_health()

        # Check hive swarm health
        hive_status = await hive.get_swarm_status()

        return {
            "status": "healthy",
            "database": db_health,
            "hive_swarm": hive_status,
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

@app.post("/api/events")
async def create_temporal_event(event: TemporalEventCreate,
                               db: TemporalDatabase = Depends(get_db)):
    """Create a new temporal event."""
    try:
        # Convert to TemporalPoint
        point = TemporalPoint(
            valid_time=event.valid_time,
            transaction_time=event.transaction_time,
            decision_time=event.decision_time,
            event_data=event.event_data
        )

        # Store in database
        event_id = await db.store_temporal_event(
            point,
            event_type=event.event_type,
            event_source=event.event_source
        )

        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "new_event",
            "event_id": str(event_id),
            "event_type": event.event_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))

        return {
            "event_id": str(event_id),
            "status": "created",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to create temporal event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/timelines")
async def create_timeline(timeline: TimelineCreate,
                         db: TemporalDatabase = Depends(get_db)):
    """Create a new temporal timeline."""
    try:
        # Convert to TemporalTimeline
        points = []
        for point_data in timeline.points:
            point = TemporalPoint(
                valid_time=point_data.valid_time,
                transaction_time=point_data.transaction_time,
                decision_time=point_data.decision_time,
                event_data=point_data.event_data
            )
            points.append(point)

        timeline_obj = TemporalTimeline(
            name=timeline.name,
            points=points
        )
        timeline_obj.description = timeline.description

        # Store in database
        timeline_id = await db.store_timeline(timeline_obj)

        return {
            "timeline_id": str(timeline_id),
            "name": timeline.name,
            "points_count": len(points),
            "status": "created",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to create timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/timelines/{timeline_id}")
async def get_timeline(timeline_id: str,
                      db: TemporalDatabase = Depends(get_db)):
    """Retrieve a temporal timeline."""
    try:
        timeline_uuid = UUID(timeline_id)
        timeline = await db.load_timeline(timeline_uuid)

        return {
            "timeline_id": timeline_id,
            "name": timeline.name,
            "description": getattr(timeline, 'description', ''),
            "points_count": len(timeline.points),
            "timeline_data": timeline.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timeline ID format")
    except Exception as e:
        logger.error(f"Failed to get timeline: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/analyze")
async def analyze_temporal_data(request: AnalysisRequest,
                               db: TemporalDatabase = Depends(get_db),
                               hive: HiveCoordinator = Depends(get_hive)):
    """Analyze temporal data using AGI hive swarm."""
    try:
        timeline = None

        # Get timeline data
        if request.timeline_id:
            timeline_uuid = UUID(request.timeline_id)
            timeline = await db.load_timeline(timeline_uuid)
        elif request.timeline_data:
            timeline = TemporalTimeline.from_dict(request.timeline_data)
        else:
            raise HTTPException(status_code=400, detail="Either timeline_id or timeline_data required")

        if request.use_hive_consensus:
            # Submit to hive swarm for consensus analysis
            task_id = await hive.submit_temporal_analysis_task(
                timeline=timeline,
                priority=request.priority
            )

            # Broadcast task submission
            await manager.broadcast(json.dumps({
                "type": "analysis_started",
                "task_id": str(task_id),
                "timeline_name": timeline.name,
                "use_consensus": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))

            return {
                "task_id": str(task_id),
                "status": "submitted_to_hive",
                "timeline_name": timeline.name,
                "use_consensus": True,
                "estimated_completion": "2-5 minutes",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        else:
            # Direct analysis without hive consensus
            anomalies = timeline.analyze_anomalies()

            return {
                "analysis_type": "direct",
                "timeline_name": timeline.name,
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
                "confidence": 0.75,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    except Exception as e:
        logger.error(f"Failed to analyze temporal data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}/status")
async def get_task_status(task_id: str,
                         hive: HiveCoordinator = Depends(get_hive)):
    """Get the status of a hive analysis task."""
    try:
        task_uuid = UUID(task_id)

        # Check active tasks
        if task_uuid in hive.active_tasks:
            task = hive.active_tasks[task_uuid]
            return HiveTaskStatus(
                task_id=task_id,
                status=task.status.value,
                progress_percentage=task.progress_percentage,
                result=task.output_data
            )

        # Check completed tasks
        for task in hive.completed_tasks:
            if task.task_id == task_uuid:
                return HiveTaskStatus(
                    task_id=task_id,
                    status=task.status.value,
                    progress_percentage=task.progress_percentage,
                    result=task.output_data
                )

        # Task not found
        raise HTTPException(status_code=404, detail="Task not found")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/anomalies")
async def get_anomalies(timeline_id: Optional[str] = None,
                       severity: Optional[str] = None,
                       limit: int = 100,
                       db: TemporalDatabase = Depends(get_db)):
    """Get temporal anomalies from the database."""
    try:
        timeline_uuid = None
        if timeline_id:
            timeline_uuid = UUID(timeline_id)

        anomalies = await db.get_anomalies(
            timeline_id=timeline_uuid,
            severity=severity,
            limit=limit
        )

        return {
            "anomalies": anomalies,
            "count": len(anomalies),
            "filters": {
                "timeline_id": timeline_id,
                "severity": severity,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hive/status")
async def get_hive_status(hive: HiveCoordinator = Depends(get_hive)):
    """Get the current status of the AGI hive swarm."""
    try:
        status = await hive.get_swarm_status()
        return status

    except Exception as e:
        logger.error(f"Failed to get hive status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/examples/timeline")
async def create_example_timeline(name: str = "Example Timeline",
                                points_count: int = 50,
                                db: TemporalDatabase = Depends(get_db)):
    """Create an example timeline with synthetic data."""
    try:
        # Generate example timeline
        timeline = generate_example_timeline()
        timeline.name = name

        # Limit points if requested
        if points_count < len(timeline.points):
            timeline.points = timeline.points[:points_count]

        # Store in database
        timeline_id = await db.store_timeline(timeline)

        return {
            "timeline_id": str(timeline_id),
            "name": name,
            "points_count": len(timeline.points),
            "timeline_data": timeline.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to create example timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "subscribe":
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))

    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Dashboard HTML (simple example)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Simple dashboard for monitoring the system."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEX TRI Temporal AGI Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .status-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .healthy { border-color: #4CAF50; background-color: #f0fdf4; }
            .warning { border-color: #FF9800; background-color: #fffbf0; }
            .error { border-color: #F44336; background-color: #fdf0f0; }
            .metric { display: inline-block; margin: 5px 10px; }
        </style>
    </head>
    <body>
        <h1>🐝 LEX TRI Temporal AGI Dashboard</h1>

        <div class="status-card healthy">
            <h3>System Status</h3>
            <div class="metric">Status: <strong>Running</strong></div>
            <div class="metric">Version: <strong>2.0.0</strong></div>
            <div class="metric">Uptime: <strong id="uptime">Loading...</strong></div>
        </div>

        <div class="status-card">
            <h3>AGI Hive Swarm</h3>
            <div id="hive-status">Loading...</div>
        </div>

        <div class="status-card">
            <h3>Database Health</h3>
            <div id="db-status">Loading...</div>
        </div>

        <div class="status-card">
            <h3>Recent Activity</h3>
            <div id="activity-log">
                <p>Connecting to real-time feed...</p>
            </div>
        </div>

        <script>
            // WebSocket connection for real-time updates
            const ws = new WebSocket(`ws://${window.location.host}/ws`);

            ws.onopen = function() {
                ws.send(JSON.stringify({type: 'subscribe'}));
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const log = document.getElementById('activity-log');
                const entry = document.createElement('p');
                entry.textContent = `${new Date().toLocaleTimeString()}: ${data.type}`;
                log.insertBefore(entry, log.firstChild);

                // Keep only last 10 entries
                while (log.children.length > 10) {
                    log.removeChild(log.lastChild);
                }
            };

            // Fetch status updates periodically
            async function updateStatus() {
                try {
                    const hiveResponse = await fetch('/api/hive/status');
                    const hiveData = await hiveResponse.json();
                    document.getElementById('hive-status').innerHTML = `
                        <div class="metric">Active Agents: <strong>${hiveData.active_agents}</strong></div>
                        <div class="metric">Pending Tasks: <strong>${hiveData.pending_tasks}</strong></div>
                        <div class="metric">Completed Tasks: <strong>${hiveData.completed_tasks}</strong></div>
                    `;

                    const healthResponse = await fetch('/health');
                    const healthData = await healthResponse.json();
                    document.getElementById('db-status').innerHTML = `
                        <div class="metric">Active Nodes: <strong>${healthData.database.active_nodes || 0}</strong></div>
                        <div class="metric">Health: <strong>${healthData.database.health_percentage || 0}%</strong></div>
                    `;
                } catch (error) {
                    console.error('Failed to update status:', error);
                }
            }

            // Update status every 30 seconds
            setInterval(updateStatus, 30000);
            updateStatus(); // Initial update
        </script>
    </body>
    </html>
    """

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global db, hive, mcp_server

    console.print("[bold green]🚀 Starting LEX TRI Temporal AGI Server[/bold green]")

    try:
        # Initialize database
        db = await get_database()
        console.print("[green]✓ Database initialized[/green]")

        # Initialize hive coordinator
        hive = await get_hive_coordinator(swarm_size=3)
        await hive.start()
        console.print("[green]✓ AGI Hive Swarm initialized[/green]")

        # Initialize MCP server (background task)
        mcp_server = LEXTRIMCPServer()
        console.print("[green]✓ MCP Server configured[/green]")

        console.print("[bold green]🎉 LEX TRI Temporal AGI Server ready![/bold green]")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        console.print(f"[red]❌ Startup failed: {e}[/red]")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    console.print("[yellow]🛑 Shutting down LEX TRI Temporal AGI Server[/yellow]")

    try:
        if hive:
            await hive.stop()
            console.print("[green]✓ Hive coordinator stopped[/green]")

        if db:
            await db.close()
            console.print("[green]✓ Database connections closed[/green]")

        console.print("[green]✓ Shutdown complete[/green]")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Main entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    console.print(f"[blue]Starting server on {host}:{port}[/blue]")

    uvicorn.run(
        "temporal_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )