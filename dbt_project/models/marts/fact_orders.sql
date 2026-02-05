select
    o.order_id,
    o.customer_id,
    o.product_id,
    o.order_timestamp,
    o.order_date,
    o.quantity,
    o.unit_price,
    o.discount_amount,
    (o.quantity * o.unit_price - o.discount_amount) as gross_revenue,
    o.channel,
    o.order_status,
    p.payment_method,
    p.payment_status,
    s.carrier,
    s.shipping_status,
    s.shipped_date,
    s.delivered_date
from {{ ref('stg_orders') }} o
left join {{ ref('stg_payments') }} p on o.payment_id = p.payment_id
left join {{ ref('stg_shipping') }} s on o.shipping_id = s.shipping_id