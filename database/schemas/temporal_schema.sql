-- LEX TRI Temporal Database Schema
-- Supports tri-temporal data model with VT/TT/DT dimensions
-- Includes AGI capabilities and hive swarm coordination

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gist";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas for organization
CREATE SCHEMA IF NOT EXISTS temporal;
CREATE SCHEMA IF NOT EXISTS agi;
CREATE SCHEMA IF NOT EXISTS hive;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set search path
SET search_path TO temporal, agi, hive, analytics, public;

-- ============================================================================
-- TEMPORAL DATA TABLES
-- ============================================================================

-- Core temporal events table with tri-temporal support
CREATE TABLE temporal.events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Tri-temporal dimensions
    valid_time_start TIMESTAMPTZ NOT NULL,
    valid_time_end TIMESTAMPTZ,
    transaction_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decision_time TIMESTAMPTZ,

    -- Event metadata
    event_type VARCHAR(100) NOT NULL,
    event_source VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) DEFAULT 'system',

    -- Event data (JSONB for flexibility)
    event_data JSONB NOT NULL DEFAULT '{}',
    metadata JSONB DEFAULT '{}',

    -- Relationships
    parent_event_id UUID REFERENCES temporal.events(event_id),
    correlation_id UUID,

    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',

    -- Temporal constraints
    CONSTRAINT valid_temporal_order CHECK (
        valid_time_start <= COALESCE(valid_time_end, valid_time_start + INTERVAL '1 year')
    ),
    CONSTRAINT transaction_after_valid CHECK (
        transaction_time >= valid_time_start - INTERVAL '1 hour'
    )
);

-- Temporal anomalies detection table
CREATE TABLE temporal.anomalies (
    anomaly_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES temporal.events(event_id),

    -- Anomaly classification
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    confidence DECIMAL(5,4) CHECK (confidence BETWEEN 0 AND 1),

    -- Temporal measurements
    temporal_drift_seconds INTEGER,
    lag_measurement_seconds INTEGER,
    out_of_order_distance INTEGER,

    -- Description and analysis
    description TEXT NOT NULL,
    analysis_data JSONB DEFAULT '{}',

    -- Resolution tracking
    status VARCHAR(20) DEFAULT 'detected' CHECK (status IN ('detected', 'investigating', 'resolved', 'false_positive')),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,

    -- Audit
    detected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    detected_by VARCHAR(100) DEFAULT 'system'
);

-- Temporal timelines for grouping related events
CREATE TABLE temporal.timelines (
    timeline_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Timeline metadata
    timeline_type VARCHAR(50) DEFAULT 'system',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'paused')),

    -- Temporal bounds
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,

    -- Configuration
    config JSONB DEFAULT '{}',

    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system'
);

-- Link events to timelines
CREATE TABLE temporal.timeline_events (
    timeline_id UUID NOT NULL REFERENCES temporal.timelines(timeline_id),
    event_id UUID NOT NULL REFERENCES temporal.events(event_id),
    sequence_number INTEGER,

    PRIMARY KEY (timeline_id, event_id)
);

-- ============================================================================
-- AGI SYSTEM TABLES
-- ============================================================================

-- AGI agents and their capabilities
CREATE TABLE agi.agents (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    agent_type VARCHAR(100) NOT NULL,

    -- Capabilities
    capabilities JSONB NOT NULL DEFAULT '[]',
    model_config JSONB DEFAULT '{}',

    -- Status and health
    status VARCHAR(20) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'error', 'maintenance')),
    last_heartbeat TIMESTAMPTZ,

    -- Performance metrics
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    average_response_time_ms INTEGER,

    -- Configuration
    config JSONB DEFAULT '{}',

    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- AGI conversations and interactions
CREATE TABLE agi.conversations (
    conversation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agi.agents(agent_id),

    -- Conversation metadata
    title VARCHAR(500),
    context_type VARCHAR(100) DEFAULT 'general',

    -- Temporal tracking
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ,

    -- Session data
    session_data JSONB DEFAULT '{}',

    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'error'))
);

-- AGI conversation messages
CREATE TABLE agi.messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES agi.conversations(conversation_id),

    -- Message content
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text',

    -- Temporal tracking
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Vector embedding for semantic search
    embedding vector(1536)
);

-- AGI knowledge base with vector embeddings
CREATE TABLE agi.knowledge_base (
    knowledge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Content
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(100) DEFAULT 'text',

    -- Categorization
    category VARCHAR(100),
    tags TEXT[],

    -- Vector embedding for semantic search
    embedding vector(1536),

    -- Source tracking
    source_url TEXT,
    source_type VARCHAR(100),

    -- Temporal tracking
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Quality metrics
    confidence_score DECIMAL(5,4),
    usage_count INTEGER DEFAULT 0
);

-- ============================================================================
-- HIVE SWARM COORDINATION TABLES
-- ============================================================================

-- Hive nodes in the swarm
CREATE TABLE hive.nodes (
    node_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    node_type VARCHAR(100) NOT NULL,

    -- Network information
    host_address INET NOT NULL,
    port INTEGER NOT NULL,

    -- Capabilities and resources
    capabilities JSONB NOT NULL DEFAULT '[]',
    resource_limits JSONB DEFAULT '{}',
    current_load DECIMAL(5,4) DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'joining' CHECK (status IN ('joining', 'active', 'busy', 'offline', 'error')),
    last_heartbeat TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Performance
    total_tasks_completed INTEGER DEFAULT 0,
    average_task_time_ms INTEGER,

    -- Audit
    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Distributed tasks across the hive
CREATE TABLE hive.tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Task definition
    task_type VARCHAR(100) NOT NULL,
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),

    -- Assignment
    assigned_node_id UUID REFERENCES hive.nodes(node_id),
    parent_task_id UUID REFERENCES hive.tasks(task_id),

    -- Temporal tracking
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Task data
    input_data JSONB NOT NULL DEFAULT '{}',
    output_data JSONB,
    error_data JSONB,

    -- Status and progress
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'running', 'completed', 'failed', 'cancelled')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Hive swarm consensus and coordination
CREATE TABLE hive.consensus_votes (
    vote_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Voting details
    proposal_id UUID NOT NULL,
    node_id UUID NOT NULL REFERENCES hive.nodes(node_id),

    -- Vote data
    vote_type VARCHAR(50) NOT NULL,
    vote_value JSONB NOT NULL,
    confidence DECIMAL(5,4) CHECK (confidence BETWEEN 0 AND 1),

    -- Temporal
    voted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(proposal_id, node_id, vote_type)
);

-- ============================================================================
-- ANALYTICS AND MONITORING TABLES
-- ============================================================================

-- System metrics over time
CREATE TABLE analytics.metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Metric identification
    metric_name VARCHAR(200) NOT NULL,
    metric_type VARCHAR(100) NOT NULL,
    source_component VARCHAR(100),

    -- Temporal
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Values
    numeric_value DECIMAL,
    text_value TEXT,
    json_value JSONB,

    -- Metadata
    tags JSONB DEFAULT '{}',

    -- Partitioning helper
    date_partition DATE GENERATED ALWAYS AS (timestamp::DATE) STORED
);

-- Performance analytics
CREATE TABLE analytics.performance_stats (
    stat_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Component identification
    component_type VARCHAR(100) NOT NULL,
    component_id UUID,

    -- Time window
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    window_duration_seconds INTEGER,

    -- Performance metrics
    request_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    average_response_time_ms DECIMAL(10,3),
    p95_response_time_ms DECIMAL(10,3),
    p99_response_time_ms DECIMAL(10,3),

    -- Resource usage
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_mb INTEGER,

    -- Calculated at
    calculated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Temporal events indexes
CREATE INDEX idx_events_valid_time ON temporal.events USING GIST (valid_time_start, valid_time_end);
CREATE INDEX idx_events_transaction_time ON temporal.events (transaction_time);
CREATE INDEX idx_events_decision_time ON temporal.events (decision_time);
CREATE INDEX idx_events_type ON temporal.events (event_type);
CREATE INDEX idx_events_source ON temporal.events (event_source);
CREATE INDEX idx_events_correlation ON temporal.events (correlation_id);
CREATE INDEX idx_events_data_gin ON temporal.events USING GIN (event_data);

-- Anomaly detection indexes
CREATE INDEX idx_anomalies_event_id ON temporal.anomalies (event_id);
CREATE INDEX idx_anomalies_type ON temporal.anomalies (anomaly_type);
CREATE INDEX idx_anomalies_severity ON temporal.anomalies (severity);
CREATE INDEX idx_anomalies_status ON temporal.anomalies (status);
CREATE INDEX idx_anomalies_detected_at ON temporal.anomalies (detected_at);

-- AGI system indexes
CREATE INDEX idx_agents_type ON agi.agents (agent_type);
CREATE INDEX idx_agents_status ON agi.agents (status);
CREATE INDEX idx_conversations_agent ON agi.conversations (agent_id);
CREATE INDEX idx_messages_conversation ON agi.messages (conversation_id);
CREATE INDEX idx_messages_timestamp ON agi.messages (timestamp);
CREATE INDEX idx_knowledge_embedding ON agi.knowledge_base USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_knowledge_category ON agi.knowledge_base (category);
CREATE INDEX idx_knowledge_tags ON agi.knowledge_base USING GIN (tags);

-- Hive swarm indexes
CREATE INDEX idx_nodes_status ON hive.nodes (status);
CREATE INDEX idx_nodes_heartbeat ON hive.nodes (last_heartbeat);
CREATE INDEX idx_tasks_status ON hive.tasks (status);
CREATE INDEX idx_tasks_assigned_node ON hive.tasks (assigned_node_id);
CREATE INDEX idx_tasks_created_at ON hive.tasks (created_at);
CREATE INDEX idx_tasks_priority ON hive.tasks (priority);

-- Analytics indexes
CREATE INDEX idx_metrics_name_timestamp ON analytics.metrics (metric_name, timestamp);
CREATE INDEX idx_metrics_date_partition ON analytics.metrics (date_partition);
CREATE INDEX idx_performance_component ON analytics.performance_stats (component_type, component_id);
CREATE INDEX idx_performance_window ON analytics.performance_stats (window_start, window_end);

-- ============================================================================
-- TEMPORAL FUNCTIONS AND PROCEDURES
-- ============================================================================

-- Function to detect temporal anomalies
CREATE OR REPLACE FUNCTION temporal.detect_anomalies(event_id UUID)
RETURNS TABLE (
    anomaly_type TEXT,
    severity TEXT,
    description TEXT,
    confidence DECIMAL
) AS $$
BEGIN
    -- Time travel detection (TT < VT)
    RETURN QUERY
    SELECT
        'time_travel'::TEXT,
        'high'::TEXT,
        'Transaction time occurs before valid time'::TEXT,
        0.9::DECIMAL
    FROM temporal.events e
    WHERE e.event_id = detect_anomalies.event_id
    AND e.transaction_time < e.valid_time_start;

    -- Premature decision detection (DT < TT)
    RETURN QUERY
    SELECT
        'premature_decision'::TEXT,
        'medium'::TEXT,
        'Decision time occurs before transaction time'::TEXT,
        0.8::DECIMAL
    FROM temporal.events e
    WHERE e.event_id = detect_anomalies.event_id
    AND e.decision_time IS NOT NULL
    AND e.decision_time < e.transaction_time;

    -- Ingestion lag detection (significant delay between VT and TT)
    RETURN QUERY
    SELECT
        'ingestion_lag'::TEXT,
        CASE
            WHEN EXTRACT(EPOCH FROM (e.transaction_time - e.valid_time_start)) > 3600 THEN 'high'
            WHEN EXTRACT(EPOCH FROM (e.transaction_time - e.valid_time_start)) > 300 THEN 'medium'
            ELSE 'low'
        END::TEXT,
        'Significant delay between valid time and transaction time'::TEXT,
        0.7::DECIMAL
    FROM temporal.events e
    WHERE e.event_id = detect_anomalies.event_id
    AND EXTRACT(EPOCH FROM (e.transaction_time - e.valid_time_start)) > 60;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate hive swarm health
CREATE OR REPLACE FUNCTION hive.calculate_swarm_health()
RETURNS TABLE (
    total_nodes INTEGER,
    active_nodes INTEGER,
    health_percentage DECIMAL,
    avg_load DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INTEGER as total_nodes,
        COUNT(CASE WHEN status = 'active' THEN 1 END)::INTEGER as active_nodes,
        (COUNT(CASE WHEN status = 'active' THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL * 100) as health_percentage,
        AVG(current_load) as avg_load
    FROM hive.nodes
    WHERE last_heartbeat > CURRENT_TIMESTAMP - INTERVAL '5 minutes';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS FOR AUTOMATION
-- ============================================================================

-- Automatically detect anomalies when events are inserted
CREATE OR REPLACE FUNCTION temporal.auto_detect_anomalies()
RETURNS TRIGGER AS $$
DECLARE
    anomaly_record RECORD;
BEGIN
    -- Detect anomalies for the new event
    FOR anomaly_record IN
        SELECT * FROM temporal.detect_anomalies(NEW.event_id)
    LOOP
        INSERT INTO temporal.anomalies (
            event_id, anomaly_type, severity, description, confidence
        ) VALUES (
            NEW.event_id,
            anomaly_record.anomaly_type,
            anomaly_record.severity,
            anomaly_record.description,
            anomaly_record.confidence
        );
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_detect_anomalies
    AFTER INSERT ON temporal.events
    FOR EACH ROW
    EXECUTE FUNCTION temporal.auto_detect_anomalies();

-- Update timestamps automatically
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_events_updated_at
    BEFORE UPDATE ON temporal.events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_update_agents_updated_at
    BEFORE UPDATE ON agi.agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_update_nodes_updated_at
    BEFORE UPDATE ON hive.nodes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- INITIAL DATA AND CONFIGURATION
-- ============================================================================

-- Insert default timeline
INSERT INTO temporal.timelines (timeline_id, name, description, start_time)
VALUES (
    uuid_generate_v4(),
    'System Default Timeline',
    'Default timeline for system events',
    CURRENT_TIMESTAMP
);

-- Insert default AGI agent
INSERT INTO agi.agents (name, agent_type, capabilities, status)
VALUES (
    'LEX TRI Temporal Agent',
    'temporal_analyzer',
    '["temporal_analysis", "anomaly_detection", "visualization", "mcp_server"]',
    'active'
);

COMMENT ON SCHEMA temporal IS 'Tri-temporal data model supporting VT/TT/DT dimensions';
COMMENT ON SCHEMA agi IS 'AGI system components including agents, conversations, and knowledge base';
COMMENT ON SCHEMA hive IS 'Distributed hive swarm coordination and task management';
COMMENT ON SCHEMA analytics IS 'System analytics, metrics, and performance monitoring';