-- One row per customer_id. Olist gives each order its own customer_id;
-- customer_unique_id is the actual person, so repeat buyers share it.
select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix                as zip_code_prefix,
    lower(trim(customer_city))          as city,
    upper(trim(customer_state))             as state
from {{ source('olist', 'customers') }}
