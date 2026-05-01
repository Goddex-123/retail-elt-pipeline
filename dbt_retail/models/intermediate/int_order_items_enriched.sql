-- =============================================================
-- int_order_items_enriched: Enriched order items with product
-- and customer details joined in.
-- =============================================================
-- Ephemeral model (not materialized) — used as building block

with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

stores as (
    select * from {{ ref('stg_stores') }}
)

select
    oi.order_item_id,
    oi.order_id,

    -- Order context
    o.order_date,
    o.order_date_day,
    o.status            as order_status,
    o.net_amount         as order_net_amount,

    -- Customer context
    o.customer_id,
    c.full_name          as customer_name,
    c.city               as customer_city,
    c.loyalty_tier,
    c.age_group,

    -- Store context
    o.store_id,
    s.store_name,
    s.region,

    -- Product context
    oi.product_id,
    p.product_name,
    p.category_id,
    p.margin_pct         as product_margin_pct,

    -- Revenue
    oi.quantity,
    oi.unit_price,
    oi.discount_pct,
    oi.line_total_gross,
    oi.line_total_net,
    oi.discount_amount,

    -- Cost
    p.cost_price * oi.quantity as line_cost

from order_items oi
left join orders o      on oi.order_id = o.order_id
left join customers c   on o.customer_id = c.customer_id
left join stores s      on o.store_id = s.store_id
left join products p    on oi.product_id = p.product_id
