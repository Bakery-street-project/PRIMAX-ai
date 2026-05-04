-- Migration: 001_create_projects_table.sql
-- Purpose: Multi-tenant projects table with project-level secrets and Stripe entitlement mapping
-- Pattern: Shared database, shared schema with Row-Level Security (RLS)
-- References:
--   - Shared tables + RLS is the recommended starting point for 90% of SaaS products
--   - Composite indexes on (tenant_id, queried_columns) prevent full-table scans before RLS filters
--   - Stripe entitlements map Price IDs to feature flags via a lookup table

-- ============================================================
-- ENUMS
-- ============================================================

CREATE TYPE project_status AS ENUM (
  'active',
  'archived',
  'suspended'
);

CREATE TYPE secret_rotation_policy AS ENUM (
  'manual',
  '30_days',
  '60_days',
  '90_days'
);

CREATE TYPE entitlement_scope AS ENUM (
  'project',
  'tenant'
);

-- ============================================================
-- TENANTS (organization-level isolation root)
-- ============================================================

CREATE TABLE IF NOT EXISTS tenants (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug            VARCHAR(63) UNIQUE NOT NULL,          -- subdomain / URL identifier
  name            VARCHAR(255) NOT NULL,
  stripe_customer_id TEXT UNIQUE,                       -- Stripe Customer object (cus_...)
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at      TIMESTAMPTZ
);

-- ============================================================
-- SUBSCRIPTION_PLANS (local cache of Stripe Price catalog)
-- ============================================================

CREATE TABLE IF NOT EXISTS subscription_plans (
  id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  stripe_price_id TEXT UNIQUE NOT NULL,                 -- Stripe Price ID (price_...)
  stripe_product_id TEXT NOT NULL,                      -- Stripe Product ID (prod_...)
  name            VARCHAR(255) NOT NULL,
  description     TEXT,
  plan_tier       VARCHAR(50) NOT NULL,                 -- 'free', 'starter', 'pro', 'enterprise'
  is_active       BOOLEAN NOT NULL DEFAULT true,
  metadata        JSONB NOT NULL DEFAULT '{}',          -- arbitrary plan metadata
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscription_plans_tier ON subscription_plans(plan_tier);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON subscription_plans(is_active) WHERE is_active = true;

-- ============================================================
-- PLAN_ENTITLEMENTS (maps Stripe prices to feature flags / limits)
-- ============================================================

CREATE TABLE IF NOT EXISTS plan_entitlements (
  id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  plan_id         BIGINT NOT NULL REFERENCES subscription_plans(id) ON DELETE CASCADE,
  feature_key     VARCHAR(100) NOT NULL,                -- e.g. 'api_access', 'sso', 'audit_log'
  feature_value   JSONB NOT NULL DEFAULT 'true'::jsonb, -- true/false, or numeric limit (e.g. {"max_projects": 50})
  scope           entitlement_scope NOT NULL DEFAULT 'tenant',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(plan_id, feature_key)
);

CREATE INDEX IF NOT EXISTS idx_plan_entitlements_plan ON plan_entitlements(plan_id);
CREATE INDEX IF NOT EXISTS idx_plan_entitlements_feature ON plan_entitlements(feature_key);

-- ============================================================
-- TENANT_SUBSCRIPTIONS (cached Stripe subscription state per tenant)
-- ============================================================

CREATE TABLE IF NOT EXISTS tenant_subscriptions (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id               UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  stripe_subscription_id  TEXT UNIQUE NOT NULL,          -- Stripe Subscription ID (sub_...)
  stripe_price_id         TEXT NOT NULL,                 -- current active Price
  status                  VARCHAR(30) NOT NULL,           -- active, trialing, past_due, canceled, unpaid, paused
  current_period_start    TIMESTAMPTZ NOT NULL,
  current_period_end      TIMESTAMPTZ NOT NULL,
  cancel_at_period_end    BOOLEAN NOT NULL DEFAULT false,
  trial_end               TIMESTAMPTZ,
  last_synced_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT valid_subscription_status CHECK (status IN (
    'active', 'trialing', 'past_due', 'canceled', 'unpaid', 'paused',
    'incomplete', 'incomplete_expired'
  ))
);

CREATE INDEX IF NOT EXISTS idx_tenant_subscriptions_tenant ON tenant_subscriptions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_subscriptions_stripe_sub ON tenant_subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_tenant_subscriptions_status ON tenant_subscriptions(status);

-- ============================================================
-- PROJECTS (core multi-tenant table with RLS)
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name            VARCHAR(255) NOT NULL,
  slug            VARCHAR(63) NOT NULL,                  -- project-scoped identifier (unique within tenant)
  description     TEXT,
  status          project_status NOT NULL DEFAULT 'active',
  stripe_price_id TEXT REFERENCES subscription_plans(stripe_price_id) ON DELETE SET NULL,  -- project-level plan override (optional)
  metadata        JSONB NOT NULL DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at      TIMESTAMPTZ,
  UNIQUE(tenant_id, slug)
);

-- Composite index: RLS still benefits from B-tree scan on the tenant partition
CREATE INDEX IF NOT EXISTS idx_projects_tenant ON projects(tenant_id);
CREATE INDEX IF NOT EXISTS idx_projects_tenant_status ON projects(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_projects_tenant_slug ON projects(tenant_id, slug);

-- ============================================================
-- PROJECT_SECRETS (encrypted secrets scoped to a project)
-- ============================================================

CREATE TABLE IF NOT EXISTS project_secrets (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name            VARCHAR(255) NOT NULL,                  -- secret identifier (e.g. 'DATABASE_URL', 'API_KEY')
  encrypted_value BYTEA NOT NULL,                         -- ciphertext (use pgcrypto or application-layer encryption)
  encryption_key_version VARCHAR(50) NOT NULL DEFAULT 'v1', -- KMS key version for rotation tracking
  description     TEXT,
  rotation_policy secret_rotation_policy NOT NULL DEFAULT 'manual',
  last_rotated_at TIMESTAMPTZ,
  expires_at      TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(project_id, name)
);

CREATE INDEX IF NOT EXISTS idx_project_secrets_project ON project_secrets(project_id);
CREATE INDEX IF NOT EXISTS idx_project_secrets_expires ON project_secrets(expires_at) WHERE expires_at IS NOT NULL;

-- ============================================================
-- PROJECT_ENTITLEMENT_OVERRIDES (project-level feature overrides)
-- Allows a project to have different entitlements than its tenant's plan
-- ============================================================

CREATE TABLE IF NOT EXISTS project_entitlement_overrides (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  feature_key     VARCHAR(100) NOT NULL,
  feature_value   JSONB NOT NULL,
  reason          TEXT,                                   -- why this override exists
  created_by      UUID,                                   -- user who set the override
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(project_id, feature_key)
);

CREATE INDEX IF NOT EXISTS idx_project_entitlement_overrides_project ON project_entitlement_overrides(project_id);
CREATE INDEX IF NOT EXISTS idx_project_entitlement_overrides_feature ON project_entitlement_overrides(feature_key);

-- ============================================================
-- STRIPE_WEBHOOK_EVENTS (idempotency table for webhook processing)
-- ============================================================

CREATE TABLE IF NOT EXISTS stripe_webhook_events (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_event_id TEXT UNIQUE NOT NULL,                  -- Stripe event ID (evt_...)
  event_type      VARCHAR(100) NOT NULL,                  -- e.g. 'entitlements.active_entitlement_summary.updated'
  tenant_id       UUID REFERENCES tenants(id),
  payload         JSONB NOT NULL DEFAULT '{}',
  processed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_type ON stripe_webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_tenant ON stripe_webhook_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_created ON stripe_webhook_events(created_at);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on all tenant-scoped tables
ALTER TABLE tenants                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_secrets           ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_entitlement_overrides ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_subscriptions      ENABLE ROW LEVEL SECURITY;

-- RLS policies for projects
-- These assume the application sets app.current_tenant_id at the start of each request:
--   SET app.current_tenant_id = '<tenant-uuid>';
-- This provides defense-in-depth: even if application code omits tenant_id filtering,
-- the database will return zero rows for cross-tenant access attempts.

CREATE POLICY tenant_isolation_projects_select ON projects
  FOR SELECT
  USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID);

CREATE POLICY tenant_isolation_projects_insert ON projects
  FOR INSERT
  WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID);

CREATE POLICY tenant_isolation_projects_update ON projects
  FOR UPDATE
  USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID)
  WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID);

CREATE POLICY tenant_isolation_projects_delete ON projects
  FOR DELETE
  USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID);

-- RLS policies for project_secrets
CREATE POLICY tenant_isolation_secrets_select ON project_secrets
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_secrets.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  );

CREATE POLICY tenant_isolation_secrets_insert ON project_secrets
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_secrets.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  );

CREATE POLICY tenant_isolation_secrets_update ON project_secrets
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_secrets.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_secrets.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  );

CREATE POLICY tenant_isolation_secrets_delete ON project_secrets
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_secrets.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  );

-- RLS policies for project_entitlement_overrides
CREATE POLICY tenant_isolation_overrides_select ON project_entitlement_overrides
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_entitlement_overrides.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  );

CREATE POLICY tenant_isolation_overrides_insert ON project_entitlement_overrides
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_entitlement_overrides.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  );

CREATE POLICY tenant_isolation_overrides_update ON project_entitlement_overrides
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_entitlement_overrides.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_entitlement_overrides.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  );

CREATE POLICY tenant_isolation_overrides_delete ON project_entitlement_overrides
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = project_entitlement_overrides.project_id
        AND projects.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID
    )
  );

-- ============================================================
-- HELPER FUNCTION: Resolve effective entitlements for a project
-- Merges tenant-level plan entitlements with project-level overrides
-- ============================================================

CREATE OR REPLACE FUNCTION resolve_project_entitlements(
  p_project_id UUID,
  p_feature_key VARCHAR(100)
) RETURNS JSONB AS $$
DECLARE
  v_tenant_id UUID;
  v_price_id TEXT;
  v_plan_id BIGINT;
  v_tenant_value JSONB;
  v_override_value JSONB;
BEGIN
  -- Get the tenant for this project
  SELECT tenant_id, COALESCE(stripe_price_id, NULL)
    INTO v_tenant_id, v_price_id
    FROM projects
    WHERE id = p_project_id;

  IF v_tenant_id IS NULL THEN
    RETURN NULL;
  END IF;

  -- Determine which price to use: project override > tenant subscription
  IF v_price_id IS NULL THEN
    SELECT ts.stripe_price_id INTO v_price_id
      FROM tenant_subscriptions ts
      WHERE ts.tenant_id = v_tenant_id
        AND ts.status IN ('active', 'trialing')
      ORDER BY ts.updated_at DESC
      LIMIT 1;
  END IF;

  IF v_price_id IS NULL THEN
    RETURN NULL;
  END IF;

  -- Get tenant-level entitlement
  SELECT pe.feature_value INTO v_tenant_value
    FROM plan_entitlements pe
    JOIN subscription_plans sp ON sp.id = pe.plan_id
    WHERE sp.stripe_price_id = v_price_id
      AND pe.feature_key = p_feature_key
    LIMIT 1;

  -- Get project-level override (takes precedence)
  SELECT feature_value INTO v_override_value
    FROM project_entitlement_overrides
    WHERE project_id = p_project_id
      AND feature_key = p_feature_key
    LIMIT 1;

  -- Override wins if present; otherwise tenant-level entitlement
  RETURN COALESCE(v_override_value, v_tenant_value);
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================
-- HELPER FUNCTION: Check if a project has a specific entitlement
-- ============================================================

CREATE OR REPLACE FUNCTION has_project_entitlement(
  p_project_id UUID,
  p_feature_key VARCHAR(100)
) RETURNS BOOLEAN AS $$
DECLARE
  v_value JSONB;
BEGIN
  v_value := resolve_project_entitlements(p_project_id, p_feature_key);

  IF v_value IS NULL THEN
    RETURN false;
  END IF;

  -- If value is a boolean, return it directly
  IF jsonb_typeof(v_value) = 'boolean' THEN
    RETURN v_value::boolean;
  END IF;

  -- If value is an object with an 'enabled' key, check that
  IF v_value ? 'enabled' THEN
    RETURN (v_value->>'enabled')::boolean;
  END IF;

  -- Default: presence of the key means enabled
  RETURN true;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================
-- HELPER FUNCTION: Check numeric limit entitlement
-- Returns true if current usage is within the plan limit
-- Usage: SELECT check_entitlement_limit('proj-uuid', 'max_projects', 15);
-- ============================================================

CREATE OR REPLACE FUNCTION check_entitlement_limit(
  p_project_id UUID,
  p_feature_key VARCHAR(100),
  p_current_usage INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
  v_value JSONB;
  v_limit INTEGER;
BEGIN
  v_value := resolve_project_entitlements(p_project_id, p_feature_key);

  IF v_value IS NULL THEN
    RETURN false;
  END IF;

  -- Check if value is a numeric limit object like {"max_projects": 50}
  IF v_value ? p_feature_key THEN
    v_limit := (v_value->>p_feature_key)::integer;
  ELSIF jsonb_typeof(v_value) = 'number' THEN
    v_limit := v_value::integer;
  ELSE
    -- Non-numeric entitlement, treat as unlimited
    RETURN true;
  END IF;

  -- -1 means unlimited
  IF v_limit = -1 THEN
    RETURN true;
  END IF;

  RETURN p_current_usage <= v_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================
-- INDEXES FOR COMMON ENTITLEMENT QUERIES
-- ============================================================

-- Expired secrets index for cron / background job cleanup
CREATE INDEX IF NOT EXISTS idx_project_secrets_expired
  ON project_secrets(expires_at)
  WHERE expires_at IS NOT NULL;

-- Secrets needing rotation soon (within 7 days)
CREATE INDEX IF NOT EXISTS idx_project_secrets_rotation_due
  ON project_secrets(last_rotated_at, rotation_policy)
  WHERE rotation_policy != 'manual';
