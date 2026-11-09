-- Seller scorecard: volume, revenue, lateness on delivered orders and review score.
with seller_orders as (
    select distinct i.seller_id, o.order_id, o.status, o.is_late, o.review_score
    from {{ ref('stg_order_items') }} i
    join {{ ref('fct_orders') }} o using (order_id)
),

revenue as (
    select seller_id, sum(price) as revenue
    from {{ ref('fct_order_items') }}
    group by seller_id
)

select
    s.seller_id,
    s.city,
    s.state,
    count(so.order_id)                                                      as orders,
    coalesce(any_value(r.revenue), 0)                                       as revenue,
    avg(case when so.status = 'delivered' then so.is_late::int end)         as late_share,
    avg(so.review_score)                                                    as avg_review_score
from {{ ref('stg_sellers') }} s
left join seller_orders so using (seller_id)
left join revenue r using (seller_id)
group by s.seller_id, s.city, s.state
