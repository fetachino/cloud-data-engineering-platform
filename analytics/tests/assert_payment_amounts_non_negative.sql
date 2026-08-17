select *
from {{ ref('fct_payments') }}
where amount < 0
