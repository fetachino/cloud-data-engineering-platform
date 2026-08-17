select
    orders.order_id,
    orders.customer_id,
    orders.order_status,
    orders.currency,
    orders.order_created_at,
    coalesce(items.order_item_count, 0) as order_item_count,
    coalesce(items.total_quantity, 0) as total_quantity,
    coalesce(items.order_item_gross_amount, 0) as order_total,
    coalesce(payments.payment_attempt_count, 0) as payment_attempt_count,
    coalesce(payments.completed_payment_amount, 0) as completed_payment_amount,
    case
        when payments.has_completed_payment = 1 then 'completed'
        when payments.has_failed_payment = 1 then 'failed'
        else 'unpaid'
    end as payment_status,
    shipments.shipment_status,
    shipments.delivered_at
from {{ ref('stg_orders') }} as orders
left join {{ ref('int_order_item_rollup') }} as items
    on orders.order_id = items.order_id
left join {{ ref('int_order_payment_summary') }} as payments
    on orders.order_id = payments.order_id
left join {{ ref('stg_shipments') }} as shipments
    on orders.order_id = shipments.order_id
