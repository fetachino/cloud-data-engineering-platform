select *
from {{ ref('fct_orders') }}
where order_total < 0
   or completed_payment_amount < 0
   or total_quantity < 0
