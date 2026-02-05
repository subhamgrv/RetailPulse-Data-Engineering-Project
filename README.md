# RetailPulse Data Engineering Project

> **An end-to-end, beginner-friendly data engineering pipeline** — from synthetic data generation to dbt-powered analytics marts, orchestrated by Apache Airflow.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Data Flow](#architecture--data-flow)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Database Schema](#database-schema)
6. [Pipeline Modules](#pipeline-modules)
   - [Data Generation](#1-data-generation)
   - [Ingestion](#2-ingestion)
   - [Staging & Transformation](#3-staging--transformation)
   - [Data Quality Checks](#4-data-quality-checks)
   - [dbt Models](#5-dbt-models)
   - [Airflow Orchestration](#6-airflow-orchestration)
7. [Configuration & Environment](#configuration--environment)
8. [Setup & Running the Project](#setup--running-the-project)
9. [Data Entities & Fields](#data-entities--fields)
10. [dbt Model Reference](#dbt-model-reference)
11. [Data Quality Rules](#data-quality-rules)
12. [Key Design Decisions](#key-design-decisions)

---

## Project Overview

**RetailPulse** is a fully self-contained, end-to-end data engineering MVP built for learning and demonstration purposes. It simulates a retail e-commerce data platform by:

- **Generating** realistic synthetic retail data using the `Faker` library
- **Ingesting** data from both flat files (CSV, JSONL) and a live REST API
- **Transforming** raw data through multiple PostgreSQL schema layers (source → raw → staging → mart)
- **Modelling** curated analytics tables using **dbt**
- **Validating** data integrity through automated quality checks
- **Orchestrating** the entire pipeline daily using **Apache Airflow**

The project covers 6 data domains: **Customers**, **Products**, **Orders**, **Payments**, **Shipping**, and **Web Events**.

---

## Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES                               │
│                                                                     │
│  scripts/generate_data.py                scripts/payments_api.py   │
│  ┌─────────────────────┐                 ┌────────────────────┐    │
│  │  Faker-generated    │                 │  FastAPI Mock API  │    │
│  │  CSV / JSONL files  │                 │  GET /payments     │    │
│  │  data/raw/          │                 │  (localhost:8000)  │    │
│  └──────────┬──────────┘                 └────────┬───────────┘    │
└─────────────┼───────────────────────────────────┼─────────────────┘
              │                                   │
              ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      INGESTION LAYER                                │
│  pipelines/ingest/                                                  │
│  ┌─────────────┐ ┌────────────┐ ┌──────────────┐ ┌─────────────┐  │
│  │  customers  │ │  products  │ │   shipping   │ │  web_events │  │
│  │  (CSV→raw)  │ │  (CSV→raw) │ │  (CSV→raw)   │ │ (JSONL→raw) │  │
│  └─────────────┘ └────────────┘ └──────────────┘ └─────────────┘  │
│  ┌─────────────┐ ┌────────────┐                                    │
│  │   orders    │ │  payments  │                                    │
│  │(source→verify)│ │(API→raw) │                                   │
│  └─────────────┘ └────────────┘                                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   STAGING / TRANSFORM LAYER                         │
│  pipelines/transform/staging_transform.py                           │
│  • Deduplication  • Type casting  • Country normalization           │
│  • Negative quantity filtering  • Date extraction                   │
│  Writes to: staging.{orders,customers,products,...}_clean           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         dbt LAYER                                   │
│  dbt_project/models/                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Staging Views (select * from staging.*_clean)              │   │
│  │  stg_orders, stg_customers, stg_products,                   │   │
│  │  stg_payments, stg_shipping, stg_web_events                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Mart Tables (materialized as TABLE)                        │   │
│  │  dim_customers, dim_products,                               │   │
│  │  fact_orders, fct_daily_sales                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION (Airflow)                          │
│  airflow/dags/retailpulse_dag.py  — runs daily (@daily)            │
│  generate_data → run_pipeline → dbt run → dbt test                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component            | Technology                   | Version   |
|----------------------|------------------------------|-----------|
| Language             | Python                       | 3.x       |
| Data manipulation    | pandas                       | 2.1.4     |
| Database             | PostgreSQL (via Docker)      | 16        |
| ORM / DB connector   | SQLAlchemy + psycopg2-binary | 1.4.54    |
| Data generation      | Faker                        | 33.1.0    |
| HTTP client          | requests                     | 2.32.3    |
| Mock Payments API    | FastAPI + Uvicorn            | 0.115.6 / 0.32.1 |
| Data transformation  | dbt-postgres                 | 1.8.2     |
| Orchestration        | Apache Airflow               | 2.11.1    |
| Containerization     | Docker / Docker Compose      | —         |
| Config management    | python-dotenv                | 1.0.1     |

---

## Project Structure

```
RetailPulse MVP Codebase/
│
├── .env                          # Environment variables (DB credentials, API URL)
├── docker-compose.yml            # Spins up PostgreSQL 16 on port 5433
├── requirements.txt              # All Python dependencies
├── README.md                     # This file
│
├── sql/
│   └── init.sql                  # DB schema initialisation (schemas + all tables)
│
├── data/
│   ├── raw/                      # Generated flat files (CSV / JSONL)
│   │   ├── customers.csv         # 200 synthetic customer records
│   │   ├── products.csv          # 50 synthetic product records
│   │   ├── shipping.csv          # 1,000 synthetic shipping records
│   │   └── web_events.jsonl      # 2,000 synthetic web event records (newline-JSON)
│   ├── staging/                  # (reserved — currently empty)
│   └── curated/                  # (reserved — currently empty)
│
├── scripts/
│   ├── generate_data.py          # Generates all synthetic datasets using Faker
│   ├── payments_api.py           # FastAPI mock server serving payment records
│   └── run_pipeline.py           # Orchestrates all ingest → transform → quality steps
│
├── pipelines/
│   ├── utils/
│   │   └── db.py                 # SQLAlchemy engine factory + write_dataframe helper
│   ├── ingest/
│   │   ├── ingest_customers.py   # Reads customers.csv → raw.customers
│   │   ├── ingest_orders.py      # Verifies source.orders row count
│   │   ├── ingest_payments.py    # Calls Payments API → raw.payments
│   │   ├── ingest_products.py    # Reads products.csv → raw.products
│   │   ├── ingest_shipping.py    # Reads shipping.csv → raw.shipping
│   │   └── ingest_web_events.py  # Reads web_events.jsonl → raw.web_events
│   ├── transform/
│   │   └── staging_transform.py  # Cleans & loads all raw → staging.*_clean tables
│   └── quality/
│       └── quality_checks.py     # SQL-based data quality report
│
├── dbt_project/
│   ├── dbt_project.yml           # dbt project config (name, profile, model paths)
│   ├── profiles.yml              # dbt connection profile (PostgreSQL, port 5432)
│   ├── .user.yml                 # dbt user preferences
│   └── models/
│       ├── schema.yml            # Column-level tests (not_null, unique, relationships)
│       ├── staging/              # Thin SELECT * views over staging tables
│       │   ├── stg_orders.sql
│       │   ├── stg_customers.sql
│       │   ├── stg_products.sql
│       │   ├── stg_payments.sql
│       │   ├── stg_shipping.sql
│       │   └── stg_web_events.sql
│       └── marts/                # Analytics-ready materialized tables
│           ├── dim_customers.sql
│           ├── dim_products.sql
│           ├── fact_orders.sql
│           └── fct_daily_sales.sql
│
└── airflow/
    └── dags/
        └── retailpulse_dag.py    # Airflow DAG: daily pipeline orchestration
```

---

## Database Schema

The PostgreSQL database (`retailpulse`) uses four schemas:

| Schema    | Purpose                                                       |
|-----------|---------------------------------------------------------------|
| `source`  | Raw transactional data written directly by data generation   |
| `raw`     | Ingested file/API data with ingestion timestamp + source file |
| `staging` | Cleaned, deduplicated, type-cast tables ready for modelling  |
| `meta`    | Pipeline run metadata and audit trail                         |

### Source Schema

| Table           | Key Columns                                                                                       |
|-----------------|---------------------------------------------------------------------------------------------------|
| `source.orders` | `order_id`, `customer_id`, `product_id`, `order_timestamp`, `quantity`, `unit_price`, `discount_amount`, `payment_id`, `shipping_id`, `channel`, `order_status` |

### Raw Schema

| Table              | Key Columns                                                                                              |
|--------------------|----------------------------------------------------------------------------------------------------------|
| `raw.customers`    | `customer_id`, `first_name`, `last_name`, `email`, `country`, `signup_date`, `customer_segment`, `ingestion_ts`, `source_file` |
| `raw.products`     | `product_id`, `product_name`, `category`, `brand`, `cost_price`, `sale_price`, `is_active`, `ingestion_ts`, `source_file` |
| `raw.shipping`     | `shipping_id`, `order_id`, `shipped_date`, `delivered_date`, `carrier`, `shipping_status`, `warehouse_location`, `ingestion_ts`, `source_file` |
| `raw.web_events`   | `event_id`, `customer_id`, `session_id`, `event_type`, `product_id`, `event_timestamp`, `page_url`, `device_type`, `traffic_source`, `ingestion_ts`, `source_file` |
| `raw.payments`     | `payment_id`, `order_id`, `payment_timestamp`, `payment_method`, `payment_status`, `amount_paid`, `currency`, `ingestion_ts`, `source_file` |

### Staging Schema

Each staging table mirrors its source/raw counterpart (via `LIKE ... INCLUDING ALL`) after cleaning:

- `staging.orders_clean` — adds `order_date` (extracted from `order_timestamp`)
- `staging.customers_clean`
- `staging.products_clean`
- `staging.shipping_clean`
- `staging.web_events_clean`
- `staging.payments_clean`

### Meta Schema

| Table                  | Columns                                                                         |
|------------------------|---------------------------------------------------------------------------------|
| `meta.pipeline_runs`   | `run_id` (serial PK), `pipeline_name`, `status`, `started_at`, `finished_at`, `message` |

---

## Pipeline Modules

### 1. Data Generation

**File:** `scripts/generate_data.py`

Uses the **Faker** library with a fixed random seed (`42`) for reproducibility. Generates:

| Dataset      | Volume | Format        | Output                                    |
|--------------|--------|---------------|-------------------------------------------|
| Customers    | 200    | CSV           | `data/raw/customers.csv`                  |
| Products     | 50     | CSV           | `data/raw/products.csv`                   |
| Orders       | 1,000  | PostgreSQL    | Written directly to `source.orders`       |
| Shipping     | 1,000  | CSV           | `data/raw/shipping.csv`                   |
| Web Events   | 2,000  | JSONL         | `data/raw/web_events.jsonl`               |

**Intentional dirty data** introduced for realism:
- Countries stored inconsistently: `"Germany"`, `"DE"`, `"germany"` — normalized in staging
- Negative quantities (`-1`) — filtered out in staging
- Zero-discount values mixed with real discounts

**Payments** data is not generated to file — it is served live by the FastAPI mock API.

---

### 2. Ingestion

**Directory:** `pipelines/ingest/`

All modules expose a `run()` function called by `scripts/run_pipeline.py`. Each module tags ingested rows with a `source_file` field for lineage tracking.

| Module                  | Source                              | Target               | Method           |
|-------------------------|-------------------------------------|----------------------|------------------|
| `ingest_customers.py`   | `data/raw/customers.csv`            | `raw.customers`      | CSV → DataFrame  |
| `ingest_products.py`    | `data/raw/products.csv`             | `raw.products`       | CSV → DataFrame  |
| `ingest_shipping.py`    | `data/raw/shipping.csv`             | `raw.shipping`       | CSV → DataFrame  |
| `ingest_web_events.py`  | `data/raw/web_events.jsonl`         | `raw.web_events`     | JSONL line-by-line |
| `ingest_payments.py`    | `http://localhost:8000/payments`    | `raw.payments`       | REST API (GET)   |
| `ingest_orders.py`      | `source.orders` (already in DB)     | —                    | Verify row count |

The **Payments API** (`scripts/payments_api.py`) is a **FastAPI** application that serves up to 1,000 dynamically generated payment records per request. It supports a `?limit=N` query parameter and must be running before `ingest_payments.py` is called.

---

### 3. Staging & Transformation

**File:** `pipelines/transform/staging_transform.py`

Reads from all `source.*` and `raw.*` tables, applies cleaning rules, truncates staging tables, and reloads them.

**Transformation rules applied:**

| Dataset      | Transformations                                                                 |
|--------------|---------------------------------------------------------------------------------|
| Orders       | Deduplicate on `order_id`; parse `order_timestamp` to UTC datetime; filter out `quantity <= 0`; extract `order_date` |
| Customers    | Deduplicate on `customer_id` (keep last); normalize `country` field             |
| Products     | Deduplicate on `product_id` (keep last)                                         |
| Shipping     | Deduplicate on `shipping_id` (keep last)                                        |
| Payments     | Deduplicate on `payment_id` (keep last); filter out `amount_paid < 0`           |
| Web Events   | Deduplicate on `event_id` (keep last)                                           |

**Country normalization mapping** (`normalize_country`):

| Input           | Normalized Output |
|-----------------|-------------------|
| `"DE"`, `"de"`, `"germany"`, `"Germany"` | `"GERMANY"` |
| `"IN"`, `"india"`, `"India"`             | `"INDIA"`   |
| `"france"`, `"France"`                   | `"FRANCE"`  |
| `null` / missing                         | `"UNKNOWN"` |

---

### 4. Data Quality Checks

**File:** `pipelines/quality/quality_checks.py`

Runs four SQL-based checks against the staging schema and prints a report:

| Check Name            | Query Logic                                                               | What It Catches                         |
|-----------------------|---------------------------------------------------------------------------|-----------------------------------------|
| `duplicate_orders`    | Orders in `staging.orders_clean` with `count(*) > 1` grouped by `order_id` | Duplicate order records after cleaning |
| `invalid_ship_dates`  | Rows where `delivered_date < shipped_date`                                | Logically impossible shipping dates     |
| `future_orders`       | Rows where `order_timestamp > now()`                                      | Orders with timestamps in the future    |
| `negative_payments`   | Rows where `amount_paid < 0`                                              | Negative payment amounts                |

Returns a dictionary of check name → count for programmatic use.

---

### 5. dbt Models

**Directory:** `dbt_project/models/`

Project: `retailpulse_dbt` | Profile: `retailpulse_dbt` | Target schema: `mart`

#### Staging Layer (materialized as **VIEW**)

Thin pass-through views over the staging schema — no transformation logic:

| Model               | Source Table                   |
|---------------------|--------------------------------|
| `stg_orders`        | `staging.orders_clean`         |
| `stg_customers`     | `staging.customers_clean`      |
| `stg_products`      | `staging.products_clean`       |
| `stg_payments`      | `staging.payments_clean`       |
| `stg_shipping`      | `staging.shipping_clean`       |
| `stg_web_events`    | `staging.web_events_clean`     |

#### Mart Layer (materialized as **TABLE**)

| Model               | Description                                                                                  |
|---------------------|----------------------------------------------------------------------------------------------|
| `dim_customers`     | Customer dimension: `customer_id`, name, email, country, signup date, segment                |
| `dim_products`      | Product dimension: `product_id`, name, category, brand, cost/sale price, active status       |
| `fact_orders`       | Central fact table joining orders + payments + shipping; computes `gross_revenue = (quantity × unit_price) − discount_amount` |
| `fct_daily_sales`   | Daily sales aggregation: `total_orders`, `total_revenue`, `avg_order_value` grouped by `order_date` |

#### dbt Tests (schema.yml)

| Model           | Column          | Tests                              |
|-----------------|-----------------|------------------------------------|
| `stg_orders`    | `order_id`      | `not_null`, `unique`               |
| `stg_customers` | `customer_id`   | `not_null`, `unique`               |
| `stg_products`  | `product_id`    | `not_null`, `unique`               |
| `fact_orders`   | `order_id`      | `not_null`, `unique`               |
| `fact_orders`   | `customer_id`   | `relationships` → `dim_customers`  |
| `fact_orders`   | `product_id`    | `relationships` → `dim_products`   |

---

### 6. Airflow Orchestration

**File:** `airflow/dags/retailpulse_dag.py`

DAG ID: `retailpulse_pipeline` | Schedule: `@daily` | Start date: `2025-01-01` | Catchup: `False`

```
generate_data  ──▶  run_pipeline  ──▶  dbt_run  ──▶  dbt_test
```

| Task ID         | Command                                        | Description                        |
|-----------------|------------------------------------------------|------------------------------------|
| `generate_data` | `python scripts/generate_data.py`              | Generates fresh synthetic datasets |
| `run_pipeline`  | `python scripts/run_pipeline.py`               | Runs all ingest + transform + QC   |
| `dbt_run`       | `cd dbt_project && dbt run --profiles-dir .`   | Builds all dbt models              |
| `dbt_test`      | `cd dbt_project && dbt test --profiles-dir .`  | Runs all dbt schema tests          |

---

## Configuration & Environment

All sensitive configuration is stored in `.env` (do **not** commit to version control):

```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
POSTGRES_DB=retailpulse
POSTGRES_USER=retailpulse
POSTGRES_PASSWORD=retailpulse
PAYMENTS_API_URL=http://localhost:8000/payments
```

> **Note:** The Docker container maps PostgreSQL's internal port `5432` to host port `5433`. The dbt `profiles.yml` connects on port `5432` (inside Docker network); adjust if connecting from host directly.

---

## Setup & Running the Project

### Prerequisites

- Docker Desktop installed and running
- Python 3.9+
- Git

### Step 1 — Install Dependencies

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### Step 2 — Start PostgreSQL

```bash
docker compose up -d
```

This starts a `postgres:16` container named `retailpulse_postgres`, exposes port `5433`, and auto-runs `sql/init.sql` to create all schemas and tables.

### Step 3 — Generate Synthetic Data

```bash
python scripts/generate_data.py
```

Outputs: `data/raw/customers.csv`, `data/raw/products.csv`, `data/raw/shipping.csv`, `data/raw/web_events.jsonl`, and writes orders directly to `source.orders`.

### Step 4 — Start the Payments API

Open a **separate terminal** and run:

```bash
uvicorn scripts.payments_api:app --reload --port 8000
```

Verify at: [http://localhost:8000/payments](http://localhost:8000/payments)

### Step 5 — Run the Full Pipeline

```bash
python scripts/run_pipeline.py
```

This sequentially runs all ingest → staging transform → quality checks and prints a quality report to stdout.

### Step 6 — Run dbt Models

```bash
cd dbt_project
dbt run --profiles-dir .
dbt test --profiles-dir .
```

### Step 7 — (Optional) Run via Airflow

If you have Apache Airflow configured, place the project root in your `AIRFLOW_HOME` or set the DAG folder appropriately, then trigger the `retailpulse_pipeline` DAG manually or let it run on its daily schedule.

---

## Data Entities & Fields

### Customers (200 records)

| Field              | Type    | Notes                                      |
|--------------------|---------|--------------------------------------------|
| `customer_id`      | text    | Format: `C0001` – `C0200`                 |
| `first_name`       | text    | Faker-generated                            |
| `last_name`        | text    | Faker-generated                            |
| `email`            | text    | Unique, Faker-generated                    |
| `country`          | text    | Intentionally inconsistent (cleaned later) |
| `signup_date`      | date    | Within last 2 years                        |
| `customer_segment` | text    | `bronze` / `silver` / `gold`              |

### Products (50 records)

| Field          | Type     | Notes                                          |
|----------------|----------|------------------------------------------------|
| `product_id`   | text     | Format: `P0001` – `P0050`                     |
| `product_name` | text     | `"Product N"`                                  |
| `category`     | text     | Electronics / Fashion / Home / Sports          |
| `brand`        | text     | Alpha / Nova / Prime / Zen                     |
| `cost_price`   | numeric  | 40–80% of `sale_price`                        |
| `sale_price`   | numeric  | $10–$500 range                                |
| `is_active`    | boolean  | ~75% active                                   |

### Orders (1,000 records — written to `source.orders`)

| Field              | Type      | Notes                                                    |
|--------------------|-----------|----------------------------------------------------------|
| `order_id`         | text      | Format: `O00001` – `O01000`                             |
| `customer_id`      | text      | FK → customers                                           |
| `product_id`       | text      | FK → products                                            |
| `order_timestamp`  | timestamp | Last 90 days, intentionally includes some negatives     |
| `quantity`         | integer   | Usually 1–3; includes `-1` (cleaned in staging)         |
| `unit_price`       | numeric   | Matches product sale price                              |
| `discount_amount`  | numeric   | $0, $5, or $10                                          |
| `payment_id`       | text      | Format: `PAY00001`                                      |
| `shipping_id`      | text      | Format: `SHIP00001`                                     |
| `channel`          | text      | organic / paid_search / social / email                  |
| `order_status`     | text      | placed / completed / cancelled                          |

### Payments (1,000 records — served via API)

| Field                | Type      | Notes                                   |
|----------------------|-----------|-----------------------------------------|
| `payment_id`         | text      | Format: `PAY00001` – `PAY01000`        |
| `order_id`           | text      | FK → orders                             |
| `payment_timestamp`  | timestamp | Last 90 days                            |
| `payment_method`     | text      | card / paypal / bank_transfer           |
| `payment_status`     | text      | paid / failed / refunded                |
| `amount_paid`        | numeric   | $10–$500                               |
| `currency`           | text      | Always `EUR`                            |

### Shipping (1,000 records)

| Field                | Type   | Notes                                              |
|----------------------|--------|----------------------------------------------------|
| `shipping_id`        | text   | Format: `SHIP00001`                               |
| `order_id`           | text   | FK → orders                                        |
| `shipped_date`       | date   | 0–3 days after order date                         |
| `delivered_date`     | date   | 1–7 days after shipped date                       |
| `carrier`            | text   | DHL / UPS / DPD                                   |
| `shipping_status`    | text   | shipped / delivered / in_transit                  |
| `warehouse_location` | text   | Berlin / Munich / Hamburg                         |

### Web Events (2,000 records)

| Field             | Type      | Notes                                               |
|-------------------|-----------|-----------------------------------------------------|
| `event_id`        | text      | Format: `E000001` – `E002000`                      |
| `customer_id`     | text      | FK → customers                                      |
| `session_id`      | text      | UUID4                                               |
| `event_type`      | text      | page_view / add_to_cart / purchase                  |
| `product_id`      | text      | FK → products                                       |
| `event_timestamp` | timestamp | Last 60 days                                        |
| `page_url`        | text      | Format: `/product/{product_id}`                    |
| `device_type`     | text      | mobile / desktop / tablet                           |
| `traffic_source`  | text      | google / facebook / direct / newsletter             |

---

## dbt Model Reference

### `fact_orders` Computed Columns

| Column          | Formula                                        |
|-----------------|------------------------------------------------|
| `gross_revenue` | `quantity × unit_price − discount_amount`      |

Joined with `stg_payments` (on `payment_id`) and `stg_shipping` (on `shipping_id`) — both as LEFT JOINs to preserve orders with missing payment/shipping data.

### `fct_daily_sales` Aggregations

| Column             | Aggregation                         |
|--------------------|-------------------------------------|
| `total_orders`     | `COUNT(DISTINCT order_id)`          |
| `total_revenue`    | `SUM(gross_revenue)`                |
| `avg_order_value`  | `AVG(gross_revenue)`                |

---

## Data Quality Rules

| Layer     | Rule                                             | Enforced By               |
|-----------|--------------------------------------------------|---------------------------|
| Staging   | No negative quantities                           | `staging_transform.py`    |
| Staging   | No negative payment amounts                      | `staging_transform.py`    |
| Staging   | Deduplicated primary keys                        | `staging_transform.py`    |
| Staging   | Country values normalized to uppercase           | `staging_transform.py`    |
| Staging   | `order_timestamp` parsed as UTC                  | `staging_transform.py`    |
| Staging   | `order_date` extracted from timestamp            | `staging_transform.py`    |
| QC Report | Duplicate orders check                           | `quality_checks.py`       |
| QC Report | Invalid shipping dates (`delivered < shipped`)   | `quality_checks.py`       |
| QC Report | Future-dated orders                              | `quality_checks.py`       |
| QC Report | Negative payment amounts                         | `quality_checks.py`       |
| dbt       | `order_id`, `customer_id`, `product_id` not null | `schema.yml` tests        |
| dbt       | Primary key uniqueness on all staging models     | `schema.yml` tests        |
| dbt       | `fact_orders` referential integrity to dimensions| `schema.yml` relationships|

---

## Key Design Decisions

- **Multi-layer PostgreSQL architecture** (`source` → `raw` → `staging` → `mart`) mimics real-world medallion/lakehouse patterns using only a relational database.
- **`write_dataframe` helper** in `pipelines/utils/db.py` uses SQLAlchemy Core instead of `pandas.to_sql()` for better control over `append` vs `replace` semantics without dropping/recreating tables.
- **dbt staging models are views** — lightweight, no storage cost, always up-to-date with staging data.
- **dbt mart models are tables** — pre-computed for fast analytical query performance.
- **Intentional data quality issues** (messy countries, negative quantities, inconsistent formats) are built into `generate_data.py` to make the cleaning pipeline non-trivial and educational.
- **Fixed random seed (`42`)** ensures reproducible data generation runs.
- **`meta.pipeline_runs` table** is provisioned for future pipeline auditing/logging (not yet populated by current code).