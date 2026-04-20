# Strange Places Analytics Dashboard

A data warehouse project built around the [Strange Places v5.2](https://www.kaggle.com/datasets/lucassteuber/strange-places-mysterious-phenomena) dataset — 354,770 georeferenced records of mysterious and natural phenomena worldwide.

## Data Source

**Dataset:** Strange Places v5.2 — Real-World Mysterious Phenomena

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

### Record Schema

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Phenomenon type (e.g. `bigfoot_sightings`, `tornadoes`) |
| `latitude` | float64 | Latitude coordinate |
| `longitude` | float64 | Longitude coordinate |
| `name` | string | Record title |
| `description` | string | Detailed description |
| `date` | string | Date of the event |

## Problem Statement

When evaluating a territory — for insurance, construction, tourism, or research — understanding its **risk and feature profile** requires combining data from dozens of separate sources. There is no single tool that overlays natural hazards (tornadoes, earthquakes, volcanoes, storms) with unique territorial features (caves, thermal springs, megaliths, shipwrecks).

This project builds a dashboard that solves this by providing a unified analytical view of natural risks and anomalous activity across regions.

## Dashboard: Natural Risk & Anomalous Activity Map

### Key Views

1. **Density Heatmap** — Interactive map with clustered phenomena. Category filters toggle layers (hazards only, landmarks only, etc.).

2. **Region Profile** — Select an area (state, country, radius) to see:
   - Category distribution (radar / bar chart)
   - Temporal trends from the `date` field — is tornado frequency increasing? Are earthquakes becoming more common?
   - Risk index — weighted score based on hazardous event density per unit area

3. **Time Trends** — Seasonality and long-term trend analysis (e.g. tornadoes by month, UFO sightings by year).

4. **Region Comparison** — Side-by-side comparison of two territories across all categories: "Where is it safer? Where is it more interesting for tourism?"

### Key Metrics

| Metric | Derived From |
|--------|-------------|
| Event density per km² by category | `latitude`, `longitude`, `category` |
| Year-over-year event frequency trend | `date`, `category` |
| Top-N most event-dense regions | geo-grid aggregation |
| Hazardous vs. neutral event ratio | `category` (risk classification) |
| Event seasonality | `date` (month extraction) |

### Target Audience

- **Insurance companies** — territorial natural risk assessment
- **Tour operators** — finding unique attractions (caves + megaliths + thermal springs)
- **Researchers** — correlation analysis (geological activity vs. anomalous observations)

## Data Warehouse Model

The warehouse follows a three-layer architecture: **STG** (staging) → **DS** (data store) → **MARTS** (data marts).

### Data Flow

```
Source (JSON)
    │
    ▼
┌──────────────────────┐
│  stg_strange_places   │  raw, as-is
└──────────┬───────────┘
           │  clean, typecast, enrich
           ▼
┌─────────────────────────────────────────┐
│  ds_dim_category  │  ds_dim_location    │
│  ds_dim_date      │  ds_fct_events      │  star schema
└──────────┬──────────────────────────────┘
           │  aggregate
           ▼
┌─────────────────────────────────────────┐
│  marts_region_profile                   │
│  marts_time_trends                      │
│  marts_geo_heatmap                      │
│  marts_region_comparison                │  dashboard-ready
└─────────────────────────────────────────┘
```

### STG — Staging Layer

Raw data loaded as-is from the source with no transformations.

| Table | Fields |
|-------|--------|
| `stg_strange_places` | `category`, `latitude`, `longitude`, `name`, `description`, `date` (all as string/raw types), `loaded_at` |

### DS — Data Store Layer

Cleaned, typecasted, and enriched data organized as a star schema.

#### Dimensions

| Table | Fields | Logic |
|-------|--------|-------|
| `ds_dim_category` | `category_id`, `category_name`, `category_group`, `source_authority` | Lookup of 14 categories classified into risk groups |
| `ds_dim_location` | `location_id`, `latitude`, `longitude`, `country`, `region`, `geo_hash` | Deduplicated coordinates enriched with reverse geocoding |
| `ds_dim_date` | `date_id`, `full_date`, `year`, `month`, `day`, `quarter`, `day_of_week`, `season` | Calendar dimension derived from the `date` field |

#### Facts

| Table | Fields | Logic |
|-------|--------|-------|
| `ds_fct_events` | `event_id`, `category_id` (FK), `location_id` (FK), `date_id` (FK), `event_name`, `event_description` | One row per phenomenon, linked to dimensions via surrogate keys |

#### Category Group Classification

| Group | Categories |
|-------|-----------|
| **hazard** | tornadoes, storm_events, earthquakes, volcanoes, fireballs |
| **landmark** | caves, megalithic_sites, ghost_towns, thermal_springs, shipwrecks, meteorite_landings |
| **anomaly** | ufo_sightings, bigfoot_sightings, haunted_places |

### MARTS — Data Marts Layer

Pre-aggregated tables optimized for specific dashboard views.

| Table | Fields | Purpose |
|-------|--------|---------|
| `marts_region_profile` | `country`, `region`, `category_group`, `category_name`, `event_count`, `density_per_km2`, `risk_index` | Region profile — event density and risk index |
| `marts_time_trends` | `year`, `month`, `season`, `category_name`, `category_group`, `event_count`, `yoy_change_pct` | Time trends — seasonality and year-over-year dynamics |
| `marts_geo_heatmap` | `geo_hash`, `latitude`, `longitude`, `category_group`, `event_count` | Heatmap data — aggregation by geo-grid cells |
| `marts_region_comparison` | `country`, `region`, `hazard_count`, `landmark_count`, `anomaly_count`, `total_count`, `risk_index`, `tourism_index` | Region comparison — hazard vs. landmark vs. anomaly breakdown |
