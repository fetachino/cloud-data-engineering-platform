select *
from {{ ref('stg_shipments') }}
where shipment_status = 'delivered'
  and delivered_at is null
