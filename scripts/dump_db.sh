#!/bin/bash
set -e

# Uses standard PostgreSQL environment variables
# PGHOST, PGDATABASE, PGUSER, PGPASSWORD
pg_dump -Fc -Z 9 > dump.sql
echo "Database dumped to dump.sql"
