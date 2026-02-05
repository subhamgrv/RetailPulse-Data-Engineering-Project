select
    product_id,
    product_name,
    category,
    brand,
    cost_price,
    sale_price,
    is_active
from {{ ref('stg_products') }}