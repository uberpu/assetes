#!/bin/bash
set -e

if [ -f "dump.sql" ]; then
    pg_restore -d postgres -c -O dump.sql || echo "Restore warning: Database may not have existed yet. Ignoring..."
    echo "Database restored from dump.sql"
else
    echo "dump.sql not found, skipping restore."
fi
