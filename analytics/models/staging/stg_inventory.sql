select
    inventory_event_id,
    product_id,
    quantity_delta,
    reason,
    adjusted_at
from {{ source('operational', 'inventory') }}
