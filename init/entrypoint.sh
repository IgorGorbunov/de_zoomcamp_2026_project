#!/bin/bash
set -e

echo "=== Generating dbt profiles.yml ==="
cat > /app/dbt/profiles.yml <<EOF
strange_places_dbt:
  outputs:
    dev:
      type: postgres
      host: ${DB_HOST}
      port: ${DB_PORT}
      dbname: ${DB_NAME}
      user: ${DB_USER}
      pass: ${DB_PASSWORD}
      schema: dbt
      threads: 4
  target: dev
EOF

echo "=== Waiting for PostgreSQL ==="
until PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "  postgres is not ready yet, retrying in 2s..."
  sleep 2
done
echo "PostgreSQL is ready."

echo "=== Loading JSON data into raw schema ==="
python -u /app/injection/load_to_stg.py /app/source/strange_places_v5.2.json

echo "=== Installing dbt packages ==="
cd /app/dbt
dbt deps --profiles-dir /app/dbt

echo "=== Running dbt models ==="
dbt run --profiles-dir /app/dbt

echo "=== All done ==="
