create schema if not exists source;
create schema if not exists raw;
create schema if not exists staging;
create schema if not exists meta;

create table if not exists source.orders (
    order_id text,
    customer_id text,
    product_id text,
    order_timestamp timestamp,
    quantity integer,
    unit_price numeric(12,2),
    discount_amount numeric(12,2),
    payment_id text,
    shipping_id text,
    channel text,
    order_status text
);

create table if not exists raw.customers (
    customer_id text,
    first_name text,
    last_name text,
    email text,
    country text,
    signup_date date,
    customer_segment text,
    ingestion_ts timestamp default now(),
    source_file text
);

create table if not exists raw.products (
    product_id text,
    product_name text,
    category text,
    brand text,
    cost_price numeric(12,2),
    sale_price numeric(12,2),
    is_active boolean,
    ingestion_ts timestamp default now(),
    source_file text
);

create table if not exists raw.shipping (
    shipping_id text,
    order_id text,
    shipped_date date,
    delivered_date date,
    carrier text,
    shipping_status text,
    warehouse_location text,
    ingestion_ts timestamp default now(),
    source_file text
);

create table if not exists raw.web_events (
    event_id text,
    customer_id text,
    session_id text,
    event_type text,
    product_id text,
    event_timestamp timestamp,
    page_url text,
    device_type text,
    traffic_source text,
    ingestion_ts timestamp default now(),
    source_file text
);

create table if not exists raw.payments (
    payment_id text,
    order_id text,
    payment_timestamp timestamp,
    payment_method text,
    payment_status text,
    amount_paid numeric(12,2),
    currency text,
    ingestion_ts timestamp default now(),
    source_file text
);

create table if not exists staging.orders_clean (like source.orders including all);
alter table staging.orders_clean add column if not exists order_date date;

create table if not exists staging.customers_clean (like raw.customers including all);
create table if not exists staging.products_clean (like raw.products including all);
create table if not exists staging.shipping_clean (like raw.shipping including all);
create table if not exists staging.web_events_clean (like raw.web_events including all);
create table if not exists staging.payments_clean (like raw.payments including all);

create table if not exists meta.pipeline_runs (
    run_id serial primary key,
    pipeline_name text,
    status text,
    started_at timestamp default now(),
    finished_at timestamp,
    message text
);