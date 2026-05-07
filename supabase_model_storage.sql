-- PRIMAX AI Model Storage Schema
-- Run this in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create storage bucket for models
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'ai-models',
  'ai-models', 
  false, -- private access only
  5368709120, -- 5GB limit per model
  ARRAY['application/octet-stream', 'application/x-gzip', 'application/zip']
)
ON CONFLICT (id) DO NOTHING;

-- Create models metadata table
CREATE TABLE IF NOT EXISTS ai_models (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  model_name TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  description TEXT,
  model_type TEXT NOT NULL, -- 'coding', 'creative', 'general'
  base_model TEXT,
  file_path TEXT, -- path in storage bucket
  file_size BIGINT,
  parameters JSONB DEFAULT '{}',
  personality TEXT,
  is_active BOOLEAN DEFAULT true,
  download_count INTEGER DEFAULT 0,
  last_used TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create model usage analytics table
CREATE TABLE IF NOT EXISTS model_usage (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  model_id UUID REFERENCES ai_models(id),
  user_query TEXT,
  response_length INTEGER,
  response_time_ms INTEGER,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_models_type ON ai_models(model_type);
CREATE INDEX IF NOT EXISTS idx_models_active ON ai_models(is_active);
CREATE INDEX IF NOT EXISTS idx_usage_model ON model_usage(model_id);
CREATE INDEX IF NOT EXISTS idx_usage_created ON model_usage(created_at);

-- Insert initial model metadata
INSERT INTO ai_models (model_name, display_name, description, model_type, personality) VALUES
('Cognaize/optimus-devstral-24b-xxl-v1.0.0', 'Optimus Prime', 'Transformers-inspired coding mentor with 24B parameters', 'coding', 'Autonomous, leader, strategic, coding expert'),
('primax-dragon-coder:latest', 'Dragon Wise', 'Ancient dragon programmer combining wisdom and code', 'creative', 'Wise, mysterious, powerful, creative coding sage')
ON CONFLICT (model_name) DO UPDATE SET
  updated_at = NOW();

-- Enable RLS
ALTER TABLE ai_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_usage ENABLE ROW LEVEL SECURITY;

-- Create policies for service role access
CREATE POLICY "Service role full access models" ON ai_models
  FOR ALL USING (auth.role() = 'service_role');
  
CREATE POLICY "Service role full access usage" ON model_usage
  FOR ALL USING (auth.role() = 'service_role');

-- Create analytics views
CREATE OR REPLACE VIEW model_performance AS
SELECT 
  m.model_name,
  m.display_name,
  COUNT(u.id) as total_queries,
  AVG(u.response_time_ms) as avg_response_time,
  AVG(u.rating) as avg_rating,
  MAX(u.created_at) as last_used
FROM ai_models m
LEFT JOIN model_usage u ON m.id = u.model_id
WHERE m.is_active = true
GROUP BY m.id, m.model_name, m.display_name;

-- Grant permissions
GRANT SELECT ON ai_models TO anon, authenticated;
GRANT SELECT ON model_usage TO service_role;
GRANT SELECT ON model_performance TO anon, authenticated;

-- Create function to log model usage
CREATE OR REPLACE FUNCTION log_model_usage(
  p_model_name TEXT,
  p_query TEXT,
  p_response_length INTEGER,
  p_response_time INTEGER,
  p_rating INTEGER DEFAULT NULL,
  p_ip_address INET DEFAULT NULL,
  p_user_agent TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
  model_id UUID;
  usage_id UUID;
BEGIN
  -- Get model ID
  SELECT id INTO model_id 
  FROM ai_models 
  WHERE model_name = p_model_name AND is_active = true;
  
  IF model_id IS NULL THEN
    RAISE EXCEPTION 'Model % not found or inactive', p_model_name;
  END IF;
  
  -- Insert usage record
  INSERT INTO model_usage (
    model_id, user_query, response_length, response_time_ms, 
    rating, ip_address, user_agent
  ) VALUES (
    model_id, p_query, p_response_length, p_response_time,
    p_rating, p_ip_address, p_user_agent
  ) RETURNING id INTO usage_id;
  
  -- Update model's last_used timestamp
  UPDATE ai_models SET last_used = NOW() WHERE id = model_id;
  
  RETURN usage_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION log_model_usage(TEXT, TEXT, INTEGER, INTEGER, INTEGER, INET, TEXT) IS 'Log model usage for analytics';

SELECT 'PRIMAX AI Model Storage Setup Complete! 🐉🤖' as status;
