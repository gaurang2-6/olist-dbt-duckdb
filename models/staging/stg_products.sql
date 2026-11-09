-- Category names are Portuguese; translate with the seed. Two categories have no translation,
-- so fall back to the original name; 610 products have no category at all.
select
    p.product_id,
    p.product_category_name                                         as category_pt,
    coalesce(t.product_category_name_english,
             p.product_category_name, 'unknown')                    as category,
    cast(p.product_photos_qty as integer)                           as photos,
    cast(p.product_weight_g as integer)                             as weight_g,
    cast(p.product_length_cm as integer)
        * cast(p.product_height_cm as integer)
        * cast(p.product_width_cm as integer)                       as volume_cm3
from {{ source('olist', 'products') }} p
left join {{ ref('product_category_name_translation') }} t using (product_category_name)
