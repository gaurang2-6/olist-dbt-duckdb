-- One row per order, with what was bought, what was paid, how delivery went and the review.
with items as (
    select
        order_id,
        count(*)                    as items,
        count(distinct seller_id)   as sellers,
        sum(price)                  as items_value,
        sum(freight)                as freight_value
    from {{ ref('stg_order_items') }}
    group by order_id
),

payments as (
    select
        order_id,
        sum(amount)                     as amount_paid,
        max(installments)               as installments,
        -- the method that paid the largest share of the order
        arg_max(payment_type, amount)   as main_payment_type
    from {{ ref('stg_order_payments') }}
    group by order_id
)

select
    o.order_id,
    c.customer_unique_id,
    c.state                                                         as customer_state,
    o.status,
    o.purchased_at,
    cast(date_trunc('month', o.purchased_at) as date)               as purchase_month,
    coalesce(i.items, 0)                                            as items,
    coalesce(i.sellers, 0)                                          as sellers,
    coalesce(i.items_value, 0)                                      as items_value,
    coalesce(i.freight_value, 0)                                    as freight_value,
    coalesce(i.items_value, 0) + coalesce(i.freight_value, 0)       as order_value,
    p.amount_paid,
    p.installments,
    p.main_payment_type,
    o.delivered_at,
    o.estimated_delivery_at,
    date_diff('day', o.purchased_at, o.delivered_at)                as delivery_days,
    date_diff('day', cast(o.estimated_delivery_at as date),
                     cast(o.delivered_at as date))                  as days_late,
    o.delivered_at is not null
        and cast(o.delivered_at as date) > cast(o.estimated_delivery_at as date)
                                                                    as is_late,
    r.score                                                         as review_score
from {{ ref('stg_orders') }} o
join {{ ref('stg_customers') }} c using (customer_id)
left join items i using (order_id)
left join payments p using (order_id)
left join {{ ref('stg_order_reviews') }} r using (order_id)
