-- =============================================================
-- stg_customers: Cleaned & deduplicated customer dimension
-- =============================================================
-- Fixes: null cities, inconsistent casing, whitespace, duplicates

with raw_customers as (
    select * from {{ source('bronze', 'customers') }}
),

cleaned as (
    select
        customer_id,
        trim(first_name)                                as first_name,
        trim(last_name)                                 as last_name,
        trim(first_name) || ' ' || trim(last_name)      as full_name,
        lower(trim(email))                               as email,
        phone,
        case
            when city is null or trim(city) = '' then 'Unknown'
            else trim(initcap(city))
        end                                              as city,
        coalesce(loyalty_tier, 'Bronze')                 as loyalty_tier,
        cast(signup_date as date)                        as signup_date,
        date_of_birth,
        -- Derive age bucket for analytics
        case
            when date_of_birth is null then 'Unknown'
            when extract(year from age(current_date, date_of_birth)) < 25 then '18-24'
            when extract(year from age(current_date, date_of_birth)) < 35 then '25-34'
            when extract(year from age(current_date, date_of_birth)) < 45 then '35-44'
            when extract(year from age(current_date, date_of_birth)) < 55 then '45-54'
            else '55+'
        end                                              as age_group,
        _loaded_at,
        _batch_id,
        -- Deduplicate: keep latest loaded record per customer_id
        row_number() over (
            partition by customer_id
            order by _loaded_at desc
        )                                                as _row_num
    from raw_customers
    where customer_id is not null
)

select
    customer_id,
    first_name,
    last_name,
    full_name,
    email,
    phone,
    city,
    loyalty_tier,
    signup_date,
    date_of_birth,
    age_group,
    _loaded_at,
    _batch_id
from cleaned
where _row_num = 1
