-- =============================================================
-- dim_customers_scd2: SCD Type 2 customer dimension
-- =============================================================
-- This model represents how the SCD2 snapshot would look.
-- The actual SCD2 tracking is handled by the dbt snapshot
-- (snapshots/snap_customers.sql). This model is a convenient
-- view for downstream consumption.

with current_customers as (
    select
        customer_id,
        full_name,
        email,
        city,
        loyalty_tier,
        age_group,
        signup_date,
        _loaded_at,
        -- In a real SCD2, these would come from the snapshot
        _loaded_at                                        as valid_from,
        cast('9999-12-31' as date)                        as valid_to,
        true                                              as is_current
    from {{ ref('stg_customers') }}
)

select * from current_customers
