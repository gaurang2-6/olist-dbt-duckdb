select
    p.product_id,
    p.category,
    p.category_pt,
    p.photos,
    p.weight_g,
    p.volume_cm3,
    count(i.order_item_key)         as units_sold,
    coalesce(sum(i.price), 0)       as revenue
from {{ ref('stg_products') }} p
left join {{ ref('fct_order_items') }} i using (product_id)
group by all
