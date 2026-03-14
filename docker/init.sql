-- Create Viyapar databases if they don't exist
-- For PostgreSQL, we use CREATE DATABASE without the IF NOT EXISTS clause
-- The POSTGRES_DB env var already creates one, so this is for additional DBs
SELECT 'CREATE DATABASE viyapar' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'viyapar')\gexec
SELECT 'CREATE DATABASE viyapar_dev' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'viyapar_dev')\gexec

