select
    shipment_id,
    order_id,
    carrier,
    tracking_number,
    status as shipment_status,
    created_at as shipment_created_at,
    delivered_at
from {{ source('operational', 'shipments') }}
