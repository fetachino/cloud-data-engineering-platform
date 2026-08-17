select
    customer_id,
    lower(email) as email,
    first_name,
    last_name,
    country,
    created_at as customer_created_at
from {{ source('operational', 'customers') }}
