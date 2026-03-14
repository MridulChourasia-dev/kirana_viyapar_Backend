#!/bin/bash
# Database initialization script for Viyapar
# This script runs automatically when the PostgreSQL container starts

set -e

echo "PostgreSQL initialization started as $(whoami)"

# Extract database name from environment
DB_NAME=${POSTGRES_DB:-viyapar}

# Check if database already exists
if psql -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Database '$DB_NAME' already exists, skipping creation"
else
    echo "Creating database '$DB_NAME'..."
    psql -U "$POSTGRES_USER" -d postgres -tc "CREATE DATABASE \"$DB_NAME\" ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';"
    echo "Database '$DB_NAME' created successfully"
fi

# Create database extensions
echo "Creating database extensions..."
psql -U "$POSTGRES_USER" -d "$DB_NAME" -tc "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" || true
psql -U "$POSTGRES_USER" -d "$DB_NAME" -tc "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";" || true
psql -U "$POSTGRES_USER" -d "$DB_NAME" -tc "CREATE EXTENSION IF NOT EXISTS \"btree_gin\";" || true

echo "PostgreSQL initialization completed successfully"
