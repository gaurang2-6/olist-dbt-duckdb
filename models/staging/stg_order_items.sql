select
    order_id || '-' || order_item_id                as order_item_key,
    order_id,
    cast(order_item_id as integer)                  as item_number,
    product_id,
    seller_id,
    cast(shipping_limit_date as timestamp)          as shipping_limit_at,
    cast(price as decimal(10, 2))                   as price,
    cast(freight_value as decimal(10, 2))           as freight
from {{ source('olist', 'order_items') }}
