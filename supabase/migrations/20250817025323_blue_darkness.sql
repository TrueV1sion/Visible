/*
  # Initial Database Schema for Battlecard Platform

  1. New Tables
    - `users` - User accounts with role-based access
    - `competitors` - Competitor company information
    - `battlecards` - Main battlecard content with versioning
    - `battlecard_versions` - Version history for battlecards
    - `objections` - Sales objection library with responses
    - `objection_usage_logs` - Track objection usage and effectiveness
    - `competitor_updates` - Track competitor changes and news
    - `insights` - AI-generated insights and recommendations

  2. Enums
    - `user_role` - Admin, editor, viewer, sales, marketing roles
    - `battlecard_status` - Draft, review, published, archived states
    - `objection_category` - Pricing, features, competition, etc.
    - `insight_type` - Different types of AI insights
    - `insight_status` - Pending, applied, discarded, expired

  3. Security
    - Enable RLS on all tables
    - Add policies for role-based access control
    - Add constraints for data validation

  4. Indexes
    - Strategic indexes on frequently queried columns
    - Composite indexes for complex queries
    - Text search indexes for full-text search

  5. Functions and Triggers
    - Updated_at timestamp triggers
    - Audit logging functions
    - Search ranking functions
*/

-- Create custom types/enums
CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer', 'sales', 'marketing');
CREATE TYPE battlecard_status AS ENUM ('draft', 'review', 'published', 'archived');
CREATE TYPE objection_category AS ENUM ('pricing', 'features', 'competition', 'technical', 'implementation', 'security', 'support', 'other');
CREATE TYPE insight_type AS ENUM ('competitive_advantage', 'market_trend', 'pricing_strategy', 'feature_comparison', 'customer_feedback', 'sales_objection');
CREATE TYPE insight_status AS ENUM ('pending', 'applied', 'discarded', 'expired');

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'viewer' NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    last_login TIMESTAMPTZ,
    refresh_token TEXT,
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMPTZ,
    avatar_url VARCHAR(500),
    department VARCHAR(100),
    title VARCHAR(100),
    email_notifications BOOLEAN DEFAULT true,
    theme_preference VARCHAR(20) DEFAULT 'light',
    
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Competitors table
CREATE TABLE IF NOT EXISTS competitors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    website VARCHAR(500),
    description TEXT,
    founded_year INTEGER,
    headquarters VARCHAR(255),
    employee_count VARCHAR(100),
    funding_info JSONB,
    market_share REAL,
    revenue VARCHAR(100),
    growth_rate REAL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ,
    last_monitored TIMESTAMPTZ,
    monitoring_enabled BOOLEAN DEFAULT false,
    monitoring_keywords JSONB,
    last_analysis_date TIMESTAMPTZ,
    social_media_urls JSONB,
    tech_stack JSONB,
    
    CONSTRAINT valid_market_share CHECK (market_share >= 0 AND market_share <= 100),
    CONSTRAINT valid_founded_year CHECK (founded_year >= 1800 AND founded_year <= EXTRACT(YEAR FROM now()))
);

-- Battlecards table
CREATE TABLE IF NOT EXISTS battlecards (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status battlecard_status DEFAULT 'draft' NOT NULL,
    company_overview TEXT,
    target_market VARCHAR(255),
    competitive_analysis JSONB,
    product_features JSONB,
    pricing_structure JSONB,
    use_cases JSONB,
    objection_handling JSONB,
    winning_strategies JSONB,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    competitor_id INTEGER REFERENCES competitors(id),
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    last_modified_by_id INTEGER REFERENCES users(id),
    tags JSONB,
    ai_generated_sections JSONB,
    generation_metadata JSONB,
    view_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMPTZ
);

-- Battlecard versions table
CREATE TABLE IF NOT EXISTS battlecard_versions (
    id SERIAL PRIMARY KEY,
    battlecard_id INTEGER NOT NULL REFERENCES battlecards(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    change_summary TEXT,
    change_type VARCHAR(50),
    
    UNIQUE(battlecard_id, version_number)
);

-- Objections table
CREATE TABLE IF NOT EXISTS objections (
    id SERIAL PRIMARY KEY,
    objection TEXT NOT NULL,
    response TEXT NOT NULL,
    category objection_category NOT NULL,
    effectiveness_score REAL DEFAULT 0.0 NOT NULL,
    usage_count INTEGER DEFAULT 0 NOT NULL,
    success_rate REAL DEFAULT 0.0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ,
    last_used TIMESTAMPTZ,
    ai_generated BOOLEAN DEFAULT false NOT NULL,
    ai_model_used VARCHAR(100),
    generation_prompt TEXT,
    reviewed BOOLEAN DEFAULT false NOT NULL,
    approved BOOLEAN DEFAULT false NOT NULL,
    review_notes TEXT,
    target_industries JSONB,
    target_customer_types JSONB,
    competitor_specific VARCHAR(255),
    supporting_evidence JSONB,
    alternative_responses JSONB,
    created_by_id INTEGER REFERENCES users(id),
    reviewed_by_id INTEGER REFERENCES users(id),
    
    CONSTRAINT valid_effectiveness CHECK (effectiveness_score >= 0 AND effectiveness_score <= 1),
    CONSTRAINT valid_success_rate CHECK (success_rate >= 0 AND success_rate <= 1)
);

-- Objection usage logs table
CREATE TABLE IF NOT EXISTS objection_usage_logs (
    id SERIAL PRIMARY KEY,
    objection_id INTEGER NOT NULL REFERENCES objections(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    used_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    outcome VARCHAR(20),
    context JSONB,
    effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 5),
    feedback_notes TEXT,
    deal_size VARCHAR(50),
    customer_industry VARCHAR(100),
    customer_size VARCHAR(50)
);

-- Competitor updates table
CREATE TABLE IF NOT EXISTS competitor_updates (
    id SERIAL PRIMARY KEY,
    competitor_id INTEGER NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    update_type VARCHAR(100) NOT NULL,
    impact_level VARCHAR(50) NOT NULL,
    ai_insights TEXT,
    suggested_actions JSONB,
    confidence_score REAL,
    sources JSONB,
    source_reliability VARCHAR(20) DEFAULT 'medium',
    update_date TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    created_by_id INTEGER REFERENCES users(id),
    processed_by_ai BOOLEAN DEFAULT false,
    ai_model_used VARCHAR(100),
    processing_duration REAL
);

-- Insights table
CREATE TABLE IF NOT EXISTS insights (
    id SERIAL PRIMARY KEY,
    type insight_type NOT NULL,
    status insight_status DEFAULT 'pending' NOT NULL,
    content TEXT NOT NULL,
    confidence REAL NOT NULL,
    sources JSONB,
    suggested_actions JSONB,
    context JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    applied_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    battlecard_id INTEGER REFERENCES battlecards(id),
    competitor_id INTEGER REFERENCES competitors(id),
    ai_model_used VARCHAR(100),
    generation_prompt TEXT,
    generation_duration REAL,
    reviewed BOOLEAN DEFAULT false,
    reviewed_by_id INTEGER REFERENCES users(id),
    review_notes TEXT,
    impact_score REAL,
    application_notes TEXT,
    
    CONSTRAINT valid_confidence CHECK (confidence >= 0 AND confidence <= 1)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_competitors_name ON competitors(name);
CREATE INDEX IF NOT EXISTS idx_competitors_monitoring ON competitors(monitoring_enabled);

CREATE INDEX IF NOT EXISTS idx_battlecards_status ON battlecards(status);
CREATE INDEX IF NOT EXISTS idx_battlecards_competitor ON battlecards(competitor_id);
CREATE INDEX IF NOT EXISTS idx_battlecards_created_by ON battlecards(created_by_id);
CREATE INDEX IF NOT EXISTS idx_battlecards_created_at ON battlecards(created_at);

CREATE INDEX IF NOT EXISTS idx_battlecard_versions_battlecard ON battlecard_versions(battlecard_id);

CREATE INDEX IF NOT EXISTS idx_objections_category ON objections(category);
CREATE INDEX IF NOT EXISTS idx_objections_effectiveness ON objections(effectiveness_score);
CREATE INDEX IF NOT EXISTS idx_objections_approved ON objections(approved);

CREATE INDEX IF NOT EXISTS idx_objection_logs_objection ON objection_usage_logs(objection_id);
CREATE INDEX IF NOT EXISTS idx_objection_logs_user ON objection_usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_objection_logs_outcome ON objection_usage_logs(outcome);

CREATE INDEX IF NOT EXISTS idx_competitor_updates_competitor ON competitor_updates(competitor_id);
CREATE INDEX IF NOT EXISTS idx_competitor_updates_date ON competitor_updates(update_date);
CREATE INDEX IF NOT EXISTS idx_competitor_updates_impact ON competitor_updates(impact_level);

CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(type);
CREATE INDEX IF NOT EXISTS idx_insights_status ON insights(status);
CREATE INDEX IF NOT EXISTS idx_insights_battlecard ON insights(battlecard_id);
CREATE INDEX IF NOT EXISTS idx_insights_competitor ON insights(competitor_id);
CREATE INDEX IF NOT EXISTS idx_insights_confidence ON insights(confidence);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_battlecards_search ON battlecards USING gin(to_tsvector('english', title || ' ' || coalesce(description, '')));
CREATE INDEX IF NOT EXISTS idx_competitors_search ON competitors USING gin(to_tsvector('english', name || ' ' || coalesce(description, '')));
CREATE INDEX IF NOT EXISTS idx_objections_search ON objections USING gin(to_tsvector('english', objection || ' ' || response));

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE battlecards ENABLE ROW LEVEL SECURITY;
ALTER TABLE battlecard_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE objections ENABLE ROW LEVEL SECURITY;
ALTER TABLE objection_usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_updates ENABLE ROW LEVEL SECURITY;
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Admins can read all users" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id::text = auth.uid()::text 
            AND users.role = 'admin'
        )
    );

-- RLS Policies for competitors table
CREATE POLICY "All authenticated users can read competitors" ON competitors
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage competitors" ON competitors
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id::text = auth.uid()::text 
            AND users.role = 'admin'
        )
    );

-- RLS Policies for battlecards table
CREATE POLICY "Users can read published battlecards" ON battlecards
    FOR SELECT USING (
        status = 'published' OR 
        created_by_id::text = auth.uid()::text
    );

CREATE POLICY "Editors can create battlecards" ON battlecards
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id::text = auth.uid()::text 
            AND users.role IN ('admin', 'editor', 'marketing')
        )
    );

CREATE POLICY "Users can update own battlecards" ON battlecards
    FOR UPDATE USING (
        created_by_id::text = auth.uid()::text OR 
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id::text = auth.uid()::text 
            AND users.role IN ('admin', 'editor')
        )
    );

-- RLS Policies for objections table
CREATE POLICY "All authenticated users can read objections" ON objections
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Editors can manage objections" ON objections
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id::text = auth.uid()::text 
            AND users.role IN ('admin', 'editor', 'sales')
        )
    );

-- RLS Policies for insights table
CREATE POLICY "Users can read relevant insights" ON insights
    FOR SELECT USING (
        created_by_id::text = auth.uid()::text OR
        battlecard_id IN (
            SELECT id FROM battlecards 
            WHERE created_by_id::text = auth.uid()::text 
            OR status = 'published'
        )
    );

CREATE POLICY "Users can create insights" ON insights
    FOR INSERT WITH CHECK (created_by_id::text = auth.uid()::text);

-- Create functions for updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitors_updated_at BEFORE UPDATE ON competitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_battlecards_updated_at BEFORE UPDATE ON battlecards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_objections_updated_at BEFORE UPDATE ON objections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function for search ranking
CREATE OR REPLACE FUNCTION battlecard_search_rank(
    battlecard_row battlecards,
    search_query text
) RETURNS real AS $$
BEGIN
    RETURN (
        ts_rank(to_tsvector('english', battlecard_row.title), plainto_tsquery('english', search_query)) * 1.0 +
        ts_rank(to_tsvector('english', coalesce(battlecard_row.description, '')), plainto_tsquery('english', search_query)) * 0.8 +
        ts_rank(to_tsvector('english', coalesce(battlecard_row.company_overview, '')), plainto_tsquery('english', search_query)) * 0.6
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create audit log table for tracking changes
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSONB,
    new_values JSONB,
    changed_by INTEGER REFERENCES users(id),
    changed_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_changed_by ON audit_logs(changed_by);
CREATE INDEX IF NOT EXISTS idx_audit_logs_changed_at ON audit_logs(changed_at);

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
    current_user_id INTEGER;
BEGIN
    -- Get current user ID from application context
    SELECT nullif(current_setting('app.current_user_id', true), '')::integer INTO current_user_id;
    
    IF TG_OP = 'DELETE' THEN
        old_data = to_jsonb(OLD);
        INSERT INTO audit_logs (table_name, record_id, action, old_values, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, old_data, current_user_id);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        old_data = to_jsonb(OLD);
        new_data = to_jsonb(NEW);
        INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, old_data, new_data, current_user_id);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        new_data = to_jsonb(NEW);
        INSERT INTO audit_logs (table_name, record_id, action, new_values, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, new_data, current_user_id);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to critical tables
CREATE TRIGGER audit_battlecards AFTER INSERT OR UPDATE OR DELETE ON battlecards
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_competitors AFTER INSERT OR UPDATE OR DELETE ON competitors
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Create performance monitoring views
CREATE OR REPLACE VIEW v_battlecard_stats AS
SELECT 
    b.id,
    b.title,
    b.status,
    b.view_count,
    c.name as competitor_name,
    u.full_name as created_by_name,
    COUNT(bv.id) as version_count,
    COUNT(i.id) as insight_count,
    b.created_at,
    b.updated_at
FROM battlecards b
LEFT JOIN competitors c ON b.competitor_id = c.id
LEFT JOIN users u ON b.created_by_id = u.id
LEFT JOIN battlecard_versions bv ON b.id = bv.battlecard_id
LEFT JOIN insights i ON b.id = i.battlecard_id
GROUP BY b.id, c.name, u.full_name;

CREATE OR REPLACE VIEW v_user_activity AS
SELECT 
    u.id,
    u.email,
    u.full_name,
    u.role,
    u.last_login,
    COUNT(DISTINCT b.id) as battlecards_created,
    COUNT(DISTINCT ol.id) as objections_used,
    COUNT(DISTINCT i.id) as insights_created
FROM users u
LEFT JOIN battlecards b ON u.id = b.created_by_id
LEFT JOIN objection_usage_logs ol ON u.id = ol.user_id
LEFT JOIN insights i ON u.id = i.created_by_id
GROUP BY u.id;

-- Insert default admin user (password: admin123!)
INSERT INTO users (email, full_name, hashed_password, role, is_active)
VALUES (
    'admin@battlecard.local',
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewJdXhzOvH2Q8xSC',  -- admin123!
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert sample data for development
INSERT INTO competitors (name, website, description, market_share, revenue) VALUES
    ('TechCorp Solutions', 'https://techcorp.example.com', 'Leading enterprise software provider', 25.5, '$100M-500M'),
    ('InnovateSoft', 'https://innovatesoft.example.com', 'Cloud-native business platform', 15.2, '$50M-100M'),
    ('GlobalTech Inc', 'https://globaltech.example.com', 'International technology company', 30.8, '$500M+')
ON CONFLICT (name) DO NOTHING;

-- Insert sample objections
INSERT INTO objections (objection, response, category, effectiveness_score, reviewed, approved, created_by_id) VALUES
    (
        'Your solution is more expensive than the competition',
        'While our initial cost may be higher, our customers consistently see 25% faster ROI due to our streamlined implementation process and comprehensive support. Let me show you how the total cost of ownership actually favors our solution...',
        'pricing',
        0.85,
        true,
        true,
        1
    ),
    (
        'We already have a solution that works fine',
        'That''s great that you have a working solution! Many of our best customers started with functional systems too. The question is whether your current solution is optimized for your future growth. Let me ask you about your experience with...',
        'competition',
        0.78,
        true,
        true,
        1
    ),
    (
        'Your product seems too complex for our team',
        'I understand that concern - simplicity is crucial for adoption. That''s exactly why we designed our platform with progressive complexity. You can start with core features that deliver immediate value, then gradually adopt advanced capabilities as your team grows comfortable...',
        'technical',
        0.82,
        true,
        true,
        1
    )
ON CONFLICT DO NOTHING;