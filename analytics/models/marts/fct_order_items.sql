select
    order_items.order_item_id,
    order_items.order_id,
    orders.customer_id,
    order_items.product_id,
    order_items.quantity,
    order_items.unit_price,
    order_items.gross_item_amount,
    order_items.order_item_created_at
from {{ ref('stg_order_items') }} as order_items
inner join {{ ref('stg_orders') }} as orders
    on order_items.order_id = orders.order_id
