import os

import pandas as pd
import psycopg2
import streamlit as st


@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()
