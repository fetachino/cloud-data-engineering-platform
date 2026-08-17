select
    product_id,
    sku,
    name as product_name,
    category,
    price as list_price,
    created_at as product_created_at
from {{ source('operational', 'products') }}
