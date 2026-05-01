-- =============================================================
-- stg_stores: Store locations with region mapping
-- =============================================================

with raw_stores as (
    select * from {{ source('bronze', 'stores') }}
)

select
    store_id,
    trim(store_name)                                     as store_name,
    trim(initcap(city))                                  as city,
    trim(initcap(region))                                as region,
    lower(trim(store_type))                              as store_type,
    cast(opening_date as date)                           as opening_date,
    coalesce(is_active, true)                            as is_active,
    -- Store age in months
    extract(month from age(current_date, cast(opening_date as date)))
        + extract(year from age(current_date, cast(opening_date as date))) * 12
                                                         as store_age_months,
    _loaded_at,
    _batch_id
from raw_stores
where store_id is not null
