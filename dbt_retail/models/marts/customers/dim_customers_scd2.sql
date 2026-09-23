-- =============================================================
-- dim_customers_scd2: SCD Type 2 customer dimension
-- =============================================================
-- Reads from the dbt snapshot (snapshots/snap_customers.sql)
-- which tracks historical changes to customer attributes.
--
-- SCD Type 2 columns:
--   valid_from  — when this version of the record became active
--   valid_to    — when this version was superseded (9999-12-31 = current)
--   is_current  — true if this is the latest version
--
-- This means a single customer can have multiple rows, each
-- representing a different historical state of their attributes.

with snapshot_data as (
    select
        customer_id,
        full_name,
        email,
        city,
        loyalty_tier,
        age_group,
        signup_date,
        _loaded_at,

        -- dbt snapshot columns → friendly aliases
        dbt_valid_from                                    as valid_from,
        coalesce(dbt_valid_to, '9999-12-31'::timestamp)  as valid_to,

        -- Derive the current flag from dbt_valid_to
        case
            when dbt_valid_to is null then true
            else false
        end                                               as is_current,

        dbt_updated_at,
        dbt_scd_id

    from {{ ref('snap_customers') }}
)

select * from snapshot_data
