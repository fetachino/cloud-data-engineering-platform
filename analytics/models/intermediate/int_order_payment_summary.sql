select
    order_id,
    count(*) as payment_attempt_count,
    sum(case when payment_status = 'completed' then amount else 0 end) as completed_payment_amount,
    max(case when payment_status = 'completed' then 1 else 0 end) as has_completed_payment,
    max(case when payment_status = 'failed' then 1 else 0 end) as has_failed_payment
from {{ ref('stg_payments') }}
group by order_id
