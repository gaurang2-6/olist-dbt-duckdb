-- Category scorecard for delivered orders.
with item_orders as (
    select p.category, i.order_id, i.price, i.freight
    from {{ ref('fct_order_items') }} i
    join {{ ref('dim_products') }} p using (product_id)
)

select
    io.category,
    count(distinct io.order_id)             as orders,
    sum(io.price)                           as revenue,
    sum(io.freight) / sum(io.price)         as freight_to_price,
    avg(o.is_late::int)                     as late_share,
    avg(o.review_score)                     as avg_review_score
from item_orders io
join {{ ref('fct_orders') }} o using (order_id)
where o.status = 'delivered'
group by io.category
order by revenue desc
