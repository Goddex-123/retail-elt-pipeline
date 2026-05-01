{{
    config(
        materialized='incremental',
        unique_key='order_item_id'
    )
}}

-- =============================================================
-- fct_orders: Core fact table — one row per order line item
-- =============================================================
-- Incremental: only processes new records since last run

with enriched as (
    select * from {{ ref('int_order_items_enriched') }}
)

select
    order_item_id,
    order_id,
    customer_id,
    customer_name,
    customer_city,
    loyalty_tier,
    store_id,
    store_name,
    region,
    product_id,
    product_name,
    category_id,
    order_date,
    order_date_day,
    order_status,
    quantity,
    unit_price,
    discount_pct,
    line_total_gross,
    line_total_net,
    discount_amount,
    line_cost,
    -- Gross profit per line
    line_total_net - coalesce(line_cost, 0)               as gross_profit,
    product_margin_pct,
    current_timestamp                                     as dbt_updated_at

from enriched

{% if is_incremental() %}
where order_date > (select max(order_date) from {{ this }})
{% endif %}
