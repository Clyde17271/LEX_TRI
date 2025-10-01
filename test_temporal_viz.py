"""
Unit tests for temporal visualization module.
"""

import os
import json
import unittest
from datetime import datetime, timedelta
import tempfile

# Import modules to be tested
from temporal_viz import (
    TemporalPoint,
    TemporalTimeline,
    generate_example_timeline,
)

# Try to import visualization functions, but don't fail if matplotlib is not available
try:
    from temporal_viz import visualize_timeline
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class TestTemporalPoint(unittest.TestCase):
    """Test cases for TemporalPoint class."""
    
    def test_creation(self):
        """Test creating a temporal point."""
        now = datetime.now()
        point = TemporalPoint(
            valid_time=now,
            transaction_time=now + timedelta(seconds=30),
            decision_time=now + timedelta(minutes=1),
            event_data={"test": "data"},
            event_id="test_event_1"
        )
        
        self.assertEqual(point.valid_time, now)
        self.assertEqual(point.transaction_time, now + timedelta(seconds=30))
        self.assertEqual(point.decision_time, now + timedelta(minutes=1))
        self.assertEqual(point.event_data, {"test": "data"})
        self.assertEqual(point.event_id, "test_event_1")
    
    def test_to_dict(self):
        """Test converting a temporal point to dictionary."""
        now = datetime.now()
        point = TemporalPoint(
            valid_time=now,
            transaction_time=now,
            decision_time=now,
            event_data={"key": "value"},
            event_id="test_event"
        )
        
        point_dict = point.to_dict()
        
        self.assertEqual(point_dict["event_id"], "test_event")
        self.assertEqual(point_dict["valid_time"], now.isoformat())
        self.assertEqual(point_dict["transaction_time"], now.isoformat())
        self.assertEqual(point_dict["decision_time"], now.isoformat())
        self.assertEqual(point_dict["data"], {"key": "value"})
    
    def test_default_values(self):
        """Test default values for optional parameters."""
        now = datetime.now()
        point = TemporalPoint(
            valid_time=now,
            transaction_time=now
        )
        
        self.assertIsNone(point.decision_time)
        self.assertEqual(point.event_data, {})
        self.assertTrue(point.event_id.startswith("evt_"))


class TestTemporalTimeline(unittest.TestCase):
    """Test cases for TemporalTimeline class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.now = datetime.now()
        self.timeline = TemporalTimeline(name="Test Timeline")
        
        # Add some points to the timeline
        for i in range(3):
            point = TemporalPoint(
                valid_time=self.now + timedelta(minutes=i*10),
                transaction_time=self.now + timedelta(minutes=i*10, seconds=30),
                decision_time=self.now + timedelta(minutes=i*10, seconds=45),
                event_data={"index": i},
                event_id=f"evt_{i}"
            )
            self.timeline.add_point(point)
    
    def test_add_point(self):
        """Test adding a point to a timeline."""
        timeline = TemporalTimeline()
        self.assertEqual(len(timeline.points), 0)
        
        point = TemporalPoint(
            valid_time=self.now,
            transaction_time=self.now
        )
        timeline.add_point(point)
        
        self.assertEqual(len(timeline.points), 1)
        self.assertEqual(timeline.points[0], point)
    
    def test_json_serialization(self):
        """Test saving and loading a timeline to/from JSON."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save the timeline to JSON
            self.timeline.save_to_json(temp_path)
            
            # Check that the file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Load the timeline from JSON
            loaded_timeline = TemporalTimeline.load_from_json(temp_path)
            
            # Check that the loaded timeline has the correct properties
            self.assertEqual(loaded_timeline.name, "Test Timeline")
            self.assertEqual(len(loaded_timeline.points), 3)
            
            # Check a sample point
            original_point = self.timeline.points[0]
            loaded_point = loaded_timeline.points[0]
            
            self.assertEqual(loaded_point.event_id, original_point.event_id)
            self.assertEqual(loaded_point.valid_time.isoformat(), original_point.valid_time.isoformat())
            self.assertEqual(loaded_point.event_data, original_point.event_data)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_analyze_anomalies(self):
        """Test analyzing anomalies in a timeline."""
        # Create a timeline with intentional anomalies
        anomaly_timeline = TemporalTimeline(name="Anomaly Timeline")
        
        # Normal point
        anomaly_timeline.add_point(TemporalPoint(
            valid_time=self.now,
            transaction_time=self.now + timedelta(seconds=30),
            decision_time=self.now + timedelta(seconds=45),
            event_id="normal"
        ))
        
        # Time travel anomaly (TT before VT)
        anomaly_timeline.add_point(TemporalPoint(
            valid_time=self.now + timedelta(minutes=10),
            transaction_time=self.now + timedelta(minutes=9),  # TT before VT
            decision_time=self.now + timedelta(minutes=11),
            event_id="time_travel"
        ))
        
        # Premature decision anomaly (DT before TT)
        anomaly_timeline.add_point(TemporalPoint(
            valid_time=self.now + timedelta(minutes=20),
            transaction_time=self.now + timedelta(minutes=21),
            decision_time=self.now + timedelta(minutes=20, seconds=30),  # DT before TT
            event_id="premature"
        ))
        
        # Ingestion lag anomaly
        anomaly_timeline.add_point(TemporalPoint(
            valid_time=self.now + timedelta(minutes=30),
            transaction_time=self.now + timedelta(minutes=32),  # 2 minutes lag
            decision_time=self.now + timedelta(minutes=33),
            event_id="lag"
        ))
        
        # Analyze anomalies
        anomalies = anomaly_timeline.analyze_anomalies()
        
        # Should detect 3 anomalies: time travel, premature decision, ingestion lag
        self.assertEqual(len(anomalies), 3)
        
        # Check specific anomalies
        anomaly_types = [a["type"] for a in anomalies]
        self.assertIn("time_travel", anomaly_types)
        self.assertIn("premature_decision", anomaly_types)
        self.assertIn("ingestion_lag", anomaly_types)


class TestExampleTimeline(unittest.TestCase):
    """Test cases for the example timeline generator."""
    
    def test_generate_example(self):
        """Test generating an example timeline."""
        timeline = generate_example_timeline()
        
        # Check that the timeline has the correct name
        self.assertEqual(timeline.name, "Example Timeline")
        
        # Should have 8 points (5 normal + 3 anomalies)
        self.assertEqual(len(timeline.points), 8)
        
        # Check for anomalies
        anomalies = timeline.analyze_anomalies()
        self.assertGreaterEqual(len(anomalies), 3)


if HAS_MATPLOTLIB:
    class TestVisualization(unittest.TestCase):
        """Test cases for timeline visualization."""
        
        def test_visualization_output(self):
            """Test that visualization produces an output file."""
            timeline = generate_example_timeline()
            
            # Create a temporary file for testing
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Generate visualization
                output_path = visualize_timeline(
                    timeline,
                    output_path=temp_path,
                    show_plot=False
                )
                
                # Check that the output file exists
                self.assertTrue(os.path.exists(temp_path))
                self.assertEqual(output_path, temp_path)
                
                # Check file size is non-zero (valid image)
                self.assertGreater(os.path.getsize(temp_path), 0)
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()