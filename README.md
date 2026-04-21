# Strange Places Analytics Dashboard

A data warehouse and analytics project built around the [Strange Places v5.2](https://www.kaggle.com/datasets/lucassteuber/strange-places-mysterious-phenomena) dataset — 354,770 georeferenced records of mysterious and natural phenomena worldwide.

## Problem description

When evaluating a territory — for insurance, construction, tourism, or research — understanding its **risk and feature profile** requires combining data from dozens of separate sources (NASA, NOAA, USGS, BFRO, NUFORC, etc.). There is no single tool that overlays natural hazards (tornadoes, earthquakes, volcanoes, storms) with unique territorial features (caves, thermal springs, megaliths, shipwrecks) and anomalous activity (UFO sightings, bigfoot sightings, haunted places).

This project builds a unified analytical platform that ingests 354,770 records across 14 categories, transforms them into a star-schema data warehouse, and exposes the results through an interactive dashboard — enabling side-by-side comparison of natural risks, landmarks, and anomalies across geographic regions.

**Target audience:**
- **Insurance companies** — territorial natural risk assessment
- **Tour operators** — finding unique attractions (caves + megaliths + thermal springs)
- **Researchers** — correlation analysis (geological activity vs. anomalous observations)

## Data ingestion

The source data is a single JSON file (`strange_places_v5.2.json`, 354,770 records) from the [Strange Places](https://www.kaggle.com/datasets/lucassteuber/strange-places-mysterious-phenomena) Kaggle dataset.

A Python script (`injection/load_to_stg.py`) reads the JSON file and bulk-loads it into the `raw.strange_places` table in PostgreSQL using `psycopg2` with `execute_values` in batches of 5,000 rows. The script creates the target schema and table if they don't exist, truncates stale data, and commits in a single transaction.

| Aspect | Detail |
|--------|--------|
| Source format | JSON (single file, ~140 MB) |
| Loader | Python + psycopg2 (`execute_values`) |
| Batch size | 5,000 rows |
| Target | PostgreSQL `raw.strange_places` |

## Batch orchestration

The entire pipeline — database provisioning, data loading, dbt transformations — is orchestrated by Docker Compose as a single batch run:

1. **`postgres`** service starts and waits until healthy (pg_isready check).
2. **`init`** service runs `entrypoint.sh`, which:
   - Generates `dbt/profiles.yml` from environment variables
   - Waits for PostgreSQL to be ready
   - Runs the Python ingestion script to load JSON into the `raw` schema
   - Installs dbt packages (`dbt deps`)
   - Runs all dbt models (`dbt run`)
3. **`streamlit`** service starts only after `init` completes successfully.

This ensures a fully reproducible pipeline from a single `docker compose up` command.

## Data warehouse

PostgreSQL 16 serves as the data warehouse. The warehouse follows a three-layer architecture:

```
Source (JSON)
    │
    ▼
┌──────────────────────┐
│  stg_strange_places  │  raw, as-is (view)
└──────────┬───────────┘
           │  clean, typecast, enrich
           ▼
┌─────────────────────────────────────────┐
│  ds_dim_category  │  ds_dim_location    │
│  ds_dim_date      │  ds_fct_events      │  star schema (tables)
└──────────┬──────────────────────────────┘
           │  aggregate
           ▼
┌─────────────────────────────────────────┐
│  marts_region_profile                   │
│  marts_time_trends                      │
│  marts_geo_heatmap                      │
│  marts_region_comparison                │  dashboard-ready (tables)
└─────────────────────────────────────────┘
```

### STG — Staging Layer

Raw data loaded as-is from the source with no transformations (materialized as a view).

### DS — Data Store Layer

Cleaned, typecasted, and enriched data organized as a star schema:

- **`ds_dim_category`** — 14 categories classified into 3 groups: `hazard`, `landmark`, `anomaly`
- **`ds_dim_location`** — deduplicated coordinates with ~20 km geo-grid bucketing (geohash)
- **`ds_dim_date`** — calendar dimension (year, month, quarter, season, day of week)
- **`ds_fct_events`** — fact table, one row per phenomenon, linked to dimensions via surrogate keys

### MARTS — Data Marts Layer

Pre-aggregated tables optimized for dashboard views:

| Table | Purpose |
|-------|---------|
| `marts_region_profile` | Region profile — event density and risk index per geo-cell |
| `marts_time_trends` | Time trends — seasonality and year-over-year dynamics |
| `marts_geo_heatmap` | Heatmap — event counts by geo-grid cell and category group |
| `marts_region_comparison` | Region comparison — hazard vs. landmark vs. anomaly breakdown |

## Transformations tools

All transformations are implemented in **dbt** (dbt-core 1.11.8 + dbt-postgres 1.10.0):

- **9 models** across 3 layers (1 staging view, 4 data store tables, 4 mart tables)
- **dbt-utils** package for surrogate key generation (`generate_surrogate_key`)
- **Data quality tests** defined in `schema.yml` files (unique, not_null, accepted_values, relationships)
- Models are fully idempotent — each `dbt run` rebuilds the warehouse from scratch

| Layer | Materialization | Models |
|-------|----------------|--------|
| `stg` | view | 1 |
| `ds` | table | 4 |
| `marts` | table | 4 |

## Dashboard

The dashboard is built with **Streamlit** + **Plotly** and has 4 pages:

1. **Overview** — bar chart of events by category group, full category breakdown table
2. **Geo Heatmap** — interactive scatter map showing event density by ~20 km grid cells, filterable by category group (hazard / landmark / anomaly)
3. **Time Trends** — annual event volume line chart, seasonality bar chart, year-over-year change table (filterable by category)
4. **Region Comparison** — scatter plot of Risk Index vs. Tourism Index by region, top regions table, risk-level distribution

**Key metrics:**
- Event density per geo-grid cell by category
- Year-over-year event frequency trend
- Hazardous vs. neutral event ratio (Risk Index)
- Event seasonality
- Tourism Index (landmark event proportion per region)

The dashboard is accessible at `http://localhost:8501` after the pipeline completes.

## Technology Stack

| Layer | Tool |
|-------|------|
| Containerization | Docker, Docker Compose |
| Data ingestion | Python + psycopg2 |
| Data warehouse | PostgreSQL 16 |
| Transformations | dbt (dbt-core + dbt-postgres) |
| Dashboard | Streamlit + Plotly |

## How to Run

### Prerequisites

- Docker and Docker Compose

### Quick Start

```bash
git clone <repo-url>
cd de_zoomcamp_2026_project
```

Download the dataset file `strange_places_v5.2.json` from [Kaggle](https://www.kaggle.com/datasets/lucassteuber/strange-places-mysterious-phenomena) and place it into the `source/` directory.

Then run:

```bash
docker compose up --build
```

This single command will:
1. Start PostgreSQL and wait until it's healthy
2. Load 354,770 records from JSON into the `raw` schema
3. Run all dbt transformations (staging → data store → marts)
4. Start the Streamlit dashboard

Once complete, open the dashboard at **http://localhost:8501**.

To stop and remove containers:

```bash
docker compose down
```

To also remove the persisted database volume:

```bash
docker compose down -v
```

### Project Structure

```
de_zoomcamp_2026_project/
├── source/                          # Dataset and metadata
│   ├── strange_places_v5.2.json     # 354,770 records (gitignored)
│   ├── dataset-metadata.json        # Schema.org metadata
│   └── README.md                    # Dataset documentation
├── injection/
│   └── load_to_stg.py              # Loads JSON → PostgreSQL raw.strange_places
├── dbt/                             # dbt project
│   ├── models/
│   │   ├── stg/                     # Staging layer (views)
│   │   ├── ds/                      # Data store — star schema (tables)
│   │   └── marts/                   # Data marts — dashboard-ready (tables)
│   ├── dbt_project.yml
│   └── packages.yml                 # dbt-utils dependency
├── init/                            # Init container
│   ├── Dockerfile
│   └── entrypoint.sh               # Pipeline orchestration script
├── streamlit/                       # Dashboard
│   ├── app.py                       # Streamlit application
│   ├── db.py                        # Database connection helper
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml               # Full stack definition
└── README.md
```

## Data Source

**Dataset:** [Strange Places v5.2 — Real-World Mysterious Phenomena](https://www.kaggle.com/datasets/lucassteuber/strange-places-mysterious-phenomena)

- **Records:** 354,770 across 14 categories
- **Coverage:** Global, ~1950–2026
- **Coordinates:** 99.9% valid (354,544 georeferenced)
- **Sources:** NASA, NOAA, USGS, BFRO, NUFORC, OpenStreetMap, Megalithic Portal, Shadowlands Index
- **License:** CC BY 4.0

### Categories

| Category | Count | Source |
|----------|-------|--------|
| Tornadoes | 71,813 | NOAA |
| Caves | 70,242 | OpenStreetMap |
| UFO Sightings | 60,632 | NUFORC |
| Megalithic Sites | 60,028 | Megalithic Portal |
| Meteorite Landings | 32,186 | NASA |
| Ghost Towns | 18,154 | OpenStreetMap |
| Storm Events | 14,770 | NOAA |
| Haunted Places | 9,717 | Shadowlands Index |
| Thermal Springs | 5,003 | NOAA |
| Bigfoot Sightings | 3,797 | BFRO |
| Earthquakes | 3,742 | USGS |
| Shipwrecks | 3,653 | NOAA |
| Fireballs | 863 | NASA |
| Volcanoes | 170 | USGS |
