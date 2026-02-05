select
    customer_id,
    first_name,
    last_name,
    email,
    country,
    signup_date,
    customer_segment
from {{ ref('stg_customers') }}