-- =============================================================
-- stg_reviews: Customer reviews with sentiment categorization
-- =============================================================

with raw_reviews as (
    select * from {{ source('bronze', 'reviews') }}
)

select
    review_id,
    order_id,
    customer_id,
    product_id,
    rating,
    -- Sentiment bucket based on rating
    case
        when rating >= 4 then 'positive'
        when rating = 3 then 'neutral'
        when rating <= 2 then 'negative'
        else 'unknown'
    end                                                  as sentiment,
    review_text,
    case
        when review_text is not null and trim(review_text) != ''
        then true else false
    end                                                  as has_review_text,
    cast(review_date as timestamp)                       as review_date,
    _loaded_at,
    _batch_id
from raw_reviews
where review_id is not null
  and rating between 1 and 5
