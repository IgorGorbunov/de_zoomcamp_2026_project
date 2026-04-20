"""Load Strange Places JSON data into the stg_strange_places table in PostgreSQL."""

import json
import os
import sys
import time

import psycopg2
from psycopg2.extras import execute_values


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "strange_places_dwh")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
DB_SCHEMA = os.getenv("DB_SCHEMA", "raw")

TABLE_NAME = "strange_places"
BATCH_SIZE = 5000

CREATE_SCHEMA_SQL = f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.{TABLE_NAME} (
    category    TEXT,
    latitude    TEXT,
    longitude   TEXT,
    name        TEXT,
    description TEXT,
    date        TEXT
)
"""

TRUNCATE_SQL = f"TRUNCATE TABLE {DB_SCHEMA}.{TABLE_NAME}"

INSERT_SQL = f"""
INSERT INTO {DB_SCHEMA}.{TABLE_NAME}
    (category, latitude, longitude, name, description, date)
VALUES %s
"""


def load_json(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data):,} records from {file_path}")
    time.sleep(3)
    return data


def to_row(record: dict) -> tuple:
    return (
        record.get("category"),
        str(record.get("latitude", "")),
        str(record.get("longitude", "")),
        record.get("name"),
        record.get("description"),
        record.get("date"),
    )


def main():
    json_path = ''
    if len(sys.argv) < 2:
        print("Usage: python injection/load_to_stg.py source/strange_places_v5.2.json")
        json_path = 'source/strange_places_v5.2.json'

    if not json_path:
        json_path = sys.argv[1]
    data = load_json(json_path)

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    conn.autocommit = False
    cur = conn.cursor()

    try:
        cur.execute(CREATE_SCHEMA_SQL)
        cur.execute(CREATE_TABLE_SQL)
        cur.execute(TRUNCATE_SQL)

        rows = [to_row(r) for r in data]
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i : i + BATCH_SIZE]
            execute_values(cur, INSERT_SQL, batch)
            print(f"  inserted {min(i + BATCH_SIZE, len(rows)):,} / {len(rows):,}")
            time.sleep(3)

        conn.commit()
        print(f"Done. {len(rows):,} records loaded into {DB_SCHEMA}.{TABLE_NAME}")
        time.sleep(3)
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
