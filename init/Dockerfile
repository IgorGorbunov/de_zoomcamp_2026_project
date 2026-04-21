FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.11 \
    dbt-core==1.11.8 \
    dbt-postgres==1.10.0

WORKDIR /app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
