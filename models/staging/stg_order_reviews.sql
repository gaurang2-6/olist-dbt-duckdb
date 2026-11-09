-- The raw file has ~550 orders with more than one review (and some review_ids reused across
-- orders). Keep one review per order: the most recently answered one.
with ranked as (
    select
        review_id,
        order_id,
        cast(review_score as integer)                   as score,
        nullif(trim(review_comment_message), '')        as comment,
        cast(review_creation_date as timestamp)         as created_at,
        cast(review_answer_timestamp as timestamp)      as answered_at,
        row_number() over (
            partition by order_id
            order by cast(review_answer_timestamp as timestamp) desc, review_id
        ) as rn
    from {{ source('olist', 'order_reviews') }}
)
select review_id, order_id, score, comment is not null as has_comment, created_at, answered_at
from ranked
where rn = 1
