-- How review scores move with delivery timing, for delivered orders that were reviewed.
-- days_late < 0 means the parcel arrived before the date promised at checkout.
select
    case
        when days_late <= -10 then '1. 10+ days early'
        when days_late <= -1  then '2. 1-9 days early'
        when days_late = 0    then '3. on the promised day'
        when days_late <= 3   then '4. 1-3 days late'
        when days_late <= 7   then '5. 4-7 days late'
        else                       '6. 8+ days late'
    end                                             as delivery_bucket,
    count(*)                                        as orders,
    avg(review_score)                               as avg_review_score,
    avg((review_score <= 2)::int)                   as share_1_2_stars,
    avg((review_score = 5)::int)                    as share_5_stars
from {{ ref('fct_orders') }}
where status = 'delivered' and delivered_at is not null and review_score is not null
group by 1
order by 1
