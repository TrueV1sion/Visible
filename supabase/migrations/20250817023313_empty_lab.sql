/*
# Initial database schema

1. New Tables
   - `users` - User accounts with role-based access
   - `competitors` - Competitor information and tracking
   - `battlecards` - Main battlecard content and metadata
   - `battlecard_versions` - Version history for battlecards
   - `competitor_updates` - Tracked competitor changes
   - `objections` - Common sales objections and responses
   - `insights` - AI-generated insights and suggestions

2. Security
   - Enable RLS on all tables
   - Add policies for role-based access control
   - Create indexes for performance

3. Constraints
   - Foreign key relationships between all related tables
   - Unique constraints on critical fields
   - Check constraints for data validation
*/

-- Create enum types
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    refresh_token TEXT
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
    market_share FLOAT,
    revenue VARCHAR(100),
    growth_rate FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_monitored TIMESTAMP WITH TIME ZONE
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    competitor_id INTEGER REFERENCES competitors(id),
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    last_modified_by_id INTEGER REFERENCES users(id)
);

-- Battlecard versions table
CREATE TABLE IF NOT EXISTS battlecard_versions (
    id SERIAL PRIMARY KEY,
    version_number INTEGER NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    battlecard_id INTEGER NOT NULL REFERENCES battlecards(id) ON DELETE CASCADE,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    UNIQUE(battlecard_id, version_number)
);

-- Competitor updates table
CREATE TABLE IF NOT EXISTS competitor_updates (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    update_type VARCHAR(100) NOT NULL,
    impact_level VARCHAR(50) NOT NULL,
    ai_insights TEXT,
    suggested_actions JSONB,
    sources JSONB,
    update_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    competitor_id INTEGER NOT NULL REFERENCES competitors(id) ON DELETE CASCADE
);

-- Objections table
CREATE TABLE IF NOT EXISTS objections (
    id SERIAL PRIMARY KEY,
    objection TEXT NOT NULL,
    response TEXT NOT NULL,
    category objection_category NOT NULL,
    effectiveness_score FLOAT DEFAULT 0.0 NOT NULL,
    usage_count INTEGER DEFAULT 0 NOT NULL,
    success_rate FLOAT DEFAULT 0.0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_used TIMESTAMP WITH TIME ZONE,
    ai_generated BOOLEAN DEFAULT false NOT NULL,
    reviewed BOOLEAN DEFAULT false NOT NULL
);

-- Insights table
CREATE TABLE IF NOT EXISTS insights (
    id SERIAL PRIMARY KEY,
    type insight_type NOT NULL,
    status insight_status DEFAULT 'pending' NOT NULL,
    content TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    sources JSONB,
    suggested_actions JSONB,
    context JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    battlecard_id INTEGER REFERENCES battlecards(id),
    competitor_id INTEGER REFERENCES competitors(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_competitors_name ON competitors(name);
CREATE INDEX IF NOT EXISTS idx_battlecards_status ON battlecards(status);
CREATE INDEX IF NOT EXISTS idx_battlecards_competitor ON battlecards(competitor_id);
CREATE INDEX IF NOT EXISTS idx_battlecards_created_by ON battlecards(created_by_id);
CREATE INDEX IF NOT EXISTS idx_battlecard_versions_battlecard ON battlecard_versions(battlecard_id);
CREATE INDEX IF NOT EXISTS idx_competitor_updates_competitor ON competitor_updates(competitor_id);
CREATE INDEX IF NOT EXISTS idx_competitor_updates_date ON competitor_updates(update_date);
CREATE INDEX IF NOT EXISTS idx_objections_category ON objections(category);
CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(type);
CREATE INDEX IF NOT EXISTS idx_insights_status ON insights(status);
CREATE INDEX IF NOT EXISTS idx_insights_battlecard ON insights(battlecard_id);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE battlecards ENABLE ROW LEVEL SECURITY;
ALTER TABLE battlecard_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_updates ENABLE ROW LEVEL SECURITY;
ALTER TABLE objections ENABLE ROW LEVEL SECURITY;
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Admins can read all users" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text 
            AND role = 'admin'
        )
    );

-- RLS Policies for battlecards
CREATE POLICY "Users can read published battlecards" ON battlecards
    FOR SELECT USING (status = 'published' OR created_by_id::text = auth.uid()::text);

CREATE POLICY "Editors can create battlecards" ON battlecards
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('admin', 'editor', 'marketing')
        )
    );

CREATE POLICY "Users can update own battlecards" ON battlecards
    FOR UPDATE USING (
        created_by_id::text = auth.uid()::text OR
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('admin', 'editor')
        )
    );

-- RLS Policies for competitors (read-only for most users)
CREATE POLICY "All authenticated users can read competitors" ON competitors
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage competitors" ON competitors
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text 
            AND role = 'admin'
        )
    );

-- RLS Policies for objections
CREATE POLICY "All authenticated users can read objections" ON objections
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Editors can manage objections" ON objections
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('admin', 'editor', 'sales')
        )
    );

-- RLS Policies for insights
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

-- Add check constraints
ALTER TABLE users 
    ADD CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE competitors 
    ADD CONSTRAINT valid_market_share CHECK (market_share >= 0 AND market_share <= 100);

ALTER TABLE objections 
    ADD CONSTRAINT valid_effectiveness CHECK (effectiveness_score >= 0 AND effectiveness_score <= 1);

ALTER TABLE insights 
    ADD CONSTRAINT valid_confidence CHECK (confidence >= 0 AND confidence <= 1);

-- Create default admin user (password: admin123!)
INSERT INTO users (email, full_name, hashed_password, role) 
VALUES (
    'admin@battlecard.com',
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/kTs/1w.K.',
    'admin'
) ON CONFLICT (email) DO NOTHING;