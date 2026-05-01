{% snapshot snap_customers %}
{#
    SCD Type 2 Snapshot for Customer Dimension
    ==========================================
    Tracks changes to customer attributes over time.
    When a customer's city, loyalty_tier, or other attributes change,
    this snapshot creates a new record with valid_from/valid_to dates.

    Strategy: timestamp-based (uses _loaded_at)
    Invalidation: new record closes the previous one
#}

{{
    config(
        target_schema='gold',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='_loaded_at',
        invalidate_hard_deletes=True,
    )
}}

select
    customer_id,
    full_name,
    email,
    city,
    loyalty_tier,
    age_group,
    signup_date,
    _loaded_at
from {{ ref('stg_customers') }}

{% endsnapshot %}
