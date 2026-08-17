select
    customers.customer_id,
    customers.email,
    customers.first_name,
    customers.last_name,
    customers.country,
    customers.customer_created_at,
    count(distinct orders.order_id) as order_count,
    min(orders.order_created_at) as first_order_at,
    max(orders.order_created_at) as most_recent_order_at,
    coalesce(sum(payments.completed_payment_amount), 0) as lifetime_completed_payment_amount
from {{ ref('stg_customers') }} as customers
left join {{ ref('stg_orders') }} as orders
    on customers.customer_id = orders.customer_id
left join {{ ref('int_order_payment_summary') }} as payments
    on orders.order_id = payments.order_id
group by
    customers.customer_id,
    customers.email,
    customers.first_name,
    customers.last_name,
    customers.country,
    customers.customer_created_at
