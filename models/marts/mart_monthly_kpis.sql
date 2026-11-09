-- Monthly business KPIs. Orders count by purchase month; revenue only for delivered orders.
with firsts as (
    select customer_unique_id, cast(date_trunc('month', first_order_at) as date) as first_month
    from {{ ref('dim_customers') }}
)

select
    o.purchase_month                                                    as month,
    count(*)                                                            as orders,
    count(*) filter (where o.status = 'delivered')                      as delivered_orders,
    sum(o.order_value) filter (where o.status = 'delivered')            as revenue,
    avg(o.order_value) filter (where o.status = 'delivered')            as avg_order_value,
    count(distinct o.customer_unique_id)                                as customers,
    count(distinct o.customer_unique_id)
        filter (where f.first_month = o.purchase_month)                 as new_customers,
    avg(o.is_late::int) filter (where o.status = 'delivered')           as late_share,
    avg(o.review_score)                                                 as avg_review_score
from {{ ref('fct_orders') }} o
join firsts f using (customer_unique_id)
group by o.purchase_month
order by month
