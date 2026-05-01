-- =============================================================
-- stg_promotions: Validated promotional campaigns
-- =============================================================

with raw_promotions as (
    select * from {{ source('bronze', 'promotions') }}
)

select
    promotion_id,
    trim(promotion_name)                                 as promotion_name,
    lower(trim(discount_type))                           as discount_type,
    coalesce(discount_value, 0)                          as discount_value,
    cast(start_date as date)                             as start_date,
    cast(end_date as date)                               as end_date,
    coalesce(min_order_value, 0)                         as min_order_value,
    coalesce(is_active, false)                           as is_active,
    -- Duration in days
    cast(end_date as date) - cast(start_date as date)    as duration_days,
    -- Is currently active?
    case
        when current_date between cast(start_date as date) and cast(end_date as date)
            and coalesce(is_active, false) = true
        then true
        else false
    end                                                  as is_currently_active,
    _loaded_at,
    _batch_id
from raw_promotions
where promotion_id is not null
  and cast(end_date as date) >= cast(start_date as date)  -- Valid date range
