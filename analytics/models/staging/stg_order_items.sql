select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price as gross_item_amount,
    created_at as order_item_created_at
from {{ source('operational', 'order_items') }}
