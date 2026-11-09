-- One row per real person (customer_unique_id), built from their orders.
select
    customer_unique_id,
    arg_min(customer_state, purchased_at)                       as state,
    min(purchased_at)                                           as first_order_at,
    max(purchased_at)                                           as last_order_at,
    count(*)                                                    as orders,
    count(*) filter (where status = 'delivered')                as delivered_orders,
    coalesce(sum(order_value) filter (where status = 'delivered'), 0) as lifetime_value,
    count(*) > 1                                                as is_repeat
from {{ ref('fct_orders') }}
group by customer_unique_id
