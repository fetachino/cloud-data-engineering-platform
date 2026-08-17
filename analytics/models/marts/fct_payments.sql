select
    payments.payment_id,
    payments.order_id,
    orders.customer_id,
    payments.amount,
    payments.currency,
    payments.provider,
    payments.payment_status,
    payments.failure_code,
    payments.payment_processed_at
from {{ ref('stg_payments') }} as payments
inner join {{ ref('stg_orders') }} as orders
    on payments.order_id = orders.order_id
