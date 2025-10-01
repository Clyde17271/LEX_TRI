"""
Tests for LEX TRI Exo integration functionality.
"""

import os
import json
import tempfile
from unittest import mock
from datetime import datetime

import pytest

from temporal_viz import TemporalPoint, TemporalTimeline
from exo_integration import ExoTemporalAdapter


def test_adapter_initialization():
    """Test ExoTemporalAdapter initialization."""
    # Test with default settings
    adapter = ExoTemporalAdapter()
    assert adapter.config == {}
    
    # Test with config
    config = {
        "api_key": "test_key",
        "project": "test_project",
        "timeline_name": "Test Timeline"
    }
    adapter = ExoTemporalAdapter(config=config)
    assert adapter.config == config


def test_temporal_point_conversion():
    """Test conversion between temporal points and Exo events."""
    # Create a temporal point
    vt = datetime.now()
    tt = datetime.now()
    dt = datetime.now()
    point = TemporalPoint(
        valid_time=vt,
        transaction_time=tt,
        decision_time=dt,
        event_data={"status": "test"},
        event_id="evt_test"
    )
    
    # Create adapter
    adapter = ExoTemporalAdapter()
    
    # Convert to Exo event
    event = adapter.temporal_point_to_exo_event(point)
    
    # Verify conversion
    assert event["id"] == "evt_test"
    assert event["valid_time"] == vt.isoformat()
    assert event["transaction_time"] == tt.isoformat()
    assert event["decision_time"] == dt.isoformat()
    assert event["data"] == {"status": "test"}
    assert event["type"] == "temporal_event"


def test_timeline_creation_from_exo_events():
    """Test creating a timeline from Exo events."""
    # Create mock Exo events
    class MockEvent:
        def __init__(self, vt, tt, dt=None, data=None, event_id=None):
            self.valid_time = vt.isoformat() if isinstance(vt, datetime) else vt
            self.transaction_time = tt.isoformat() if isinstance(tt, datetime) else tt
            self.decision_time = dt.isoformat() if dt and isinstance(dt, datetime) else dt
            self.data = data or {}
            self.id = event_id
    
    now = datetime.now()
    events = [
        MockEvent(now, now, data={"status": "normal"}, event_id="evt_1"),
        MockEvent(now, now, data={"status": "anomaly"}, event_id="evt_2")
    ]
    
    # Create adapter
    adapter = ExoTemporalAdapter()
    
    # Create timeline from events
    timeline = adapter.create_timeline_from_exo_events(events, name="Test Timeline")
    
    # Verify timeline
    assert timeline.name == "Test Timeline"
    assert len(timeline.points) == 2
    assert timeline.points[0].event_id == "evt_1"
    assert timeline.points[1].event_id == "evt_2"


@mock.patch('exo_integration.HAS_EXO', True)
def test_publish_timeline_with_mocks():
    """Test publishing a timeline to Exo with mocked Exo interface."""
    # Create a simple timeline
    timeline = TemporalTimeline(name="Test Timeline")
    now = datetime.now()
    timeline.add_point(TemporalPoint(valid_time=now, transaction_time=now, event_id="test_point"))
    
    # Create mock Exo interface with required methods
    mock_exo = mock.MagicMock()
    mock_exo.register_timeline.return_value = "timeline_123"
    mock_exo.get_timeline_dashboard_url.return_value = "https://exo.example.com/dashboard/timeline_123"
    
    # Create adapter with mock interface
    adapter = ExoTemporalAdapter(exo_interface=mock_exo, config={"publish_anomalies": True})
    
    # Publish timeline
    result = adapter.publish_timeline(timeline)
    
    # Verify result
    assert result["timeline_id"] == "timeline_123"
    assert result["timeline_name"] == "Test Timeline"
    assert result["point_count"] == 1
    assert result["dashboard_url"] == "https://exo.example.com/dashboard/timeline_123"
    
    # Verify mock calls
    mock_exo.register_timeline.assert_called_once()
    mock_exo.add_event_to_timeline.assert_called_once_with("timeline_123", mock.ANY)