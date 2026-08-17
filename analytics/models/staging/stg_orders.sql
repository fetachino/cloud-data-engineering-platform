select
    order_id,
    customer_id,
    status as order_status,
    currency,
    created_at as order_created_at
from {{ source('operational', 'orders') }}
