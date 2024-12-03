#!/usr/bin/env bash
set -e

# Varyanta uygun olarak veritabanlarını oluştur
export SCRIPT_PATH=/docker-entrypoint-initdb.d/scripts/
export PGPASSWORD=postgres
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    \i '${SCRIPT_PATH}db-v3.sql';
EOSQL
