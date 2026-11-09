select
    i.order_item_key,
    i.order_id,
    i.item_number,
    i.product_id,
    i.seller_id,
    o.purchased_at,
    i.price,
    i.freight
from {{ ref('stg_order_items') }} i
join {{ ref('stg_orders') }} o using (order_id)
