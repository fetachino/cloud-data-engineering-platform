select
    products.product_id,
    products.sku,
    products.product_name,
    products.category,
    products.list_price,
    products.product_created_at,
    coalesce(sum(order_items.quantity), 0) as units_ordered,
    coalesce(sum(order_items.gross_item_amount), 0) as gross_ordered_amount,
    coalesce(sum(inventory.quantity_delta), 0) as net_inventory_delta
from {{ ref('stg_products') }} as products
left join {{ ref('stg_order_items') }} as order_items
    on products.product_id = order_items.product_id
left join {{ ref('stg_inventory') }} as inventory
    on products.product_id = inventory.product_id
group by
    products.product_id,
    products.sku,
    products.product_name,
    products.category,
    products.list_price,
    products.product_created_at
