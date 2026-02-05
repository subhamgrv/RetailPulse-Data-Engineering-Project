select
    order_date,
    count(distinct order_id) as total_orders,
    sum(gross_revenue) as total_revenue,
    avg(gross_revenue) as avg_order_value
from {{ ref('fact_orders') }}
group by 1
order by 1