select
    order_id,
    count(*) as order_item_count,
    sum(quantity) as total_quantity,
    sum(gross_item_amount) as order_item_gross_amount
from {{ ref('stg_order_items') }}
group by order_id
