-- =============================================================
-- int_customer_orders: Customer-level order aggregations
-- =============================================================

with enriched as (
    select * from {{ ref('int_order_items_enriched') }}
),

customer_agg as (
    select
        customer_id,
        customer_name,
        customer_city,
        loyalty_tier,
        age_group,

        count(distinct order_id)                         as total_orders,
        sum(line_total_net)                               as total_revenue,
        avg(line_total_net)                               as avg_order_value,
        min(order_date)                                   as first_order_date,
        max(order_date)                                   as last_order_date,
        count(distinct product_id)                        as unique_products_bought,
        sum(quantity)                                      as total_items_bought,

        -- Recency: days since last order
        current_date - max(order_date_day)                as days_since_last_order

    from enriched
    where order_status = 'completed'
    group by 1, 2, 3, 4, 5
)

select * from customer_agg
