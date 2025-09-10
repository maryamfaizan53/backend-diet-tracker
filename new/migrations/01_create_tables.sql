-- sql
CREATE TABLE IF NOT EXISTS users_profiles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  supabase_id text NOT NULL UNIQUE,
  email text,
  full_name text,
  birth_date date,
  gender text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_users_profiles_supabase_id ON users_profiles(supabase_id);

CREATE TABLE IF NOT EXISTS health_insights (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users_profiles(id) ON DELETE CASCADE,
  request_payload jsonb NOT NULL,
  agents_output jsonb NOT NULL,
  aggregated_output text NOT NULL,
  confidence numeric NOT NULL,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_health_insights_user_id ON health_insights(user_id);
