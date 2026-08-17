select
    payment_id,
    order_id,
    amount,
    currency,
    provider,
    status as payment_status,
    failure_code,
    processed_at as payment_processed_at
from {{ source('operational', 'payments') }}
