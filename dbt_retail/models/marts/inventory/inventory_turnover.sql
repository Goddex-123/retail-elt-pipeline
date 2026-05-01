-- =============================================================
-- inventory_turnover: Product turnover ratio by category
-- =============================================================
-- Turnover ratio = units sold / avg inventory on hand

with sales as (
    select
        product_id,
        sum(quantity)                                      as total_units_sold
    from {{ ref('fct_orders') }}
    where order_status = 'completed'
    group by 1
),

avg_inventory as (
    select
        product_id,
        avg(quantity_on_hand)                              as avg_stock
    from {{ ref('stg_inventory') }}
    group by 1
),

products as (
    select product_id, product_name, category_id
    from {{ ref('stg_products') }}
)

select
    p.product_id,
    p.product_name,
    p.category_id,
    coalesce(s.total_units_sold, 0)                        as total_units_sold,
    round(coalesce(ai.avg_stock, 0), 1)                    as avg_stock_on_hand,

    -- Turnover ratio
    case
        when coalesce(ai.avg_stock, 0) > 0
        then round(coalesce(s.total_units_sold, 0)::numeric / ai.avg_stock, 2)
        else 0
    end                                                    as turnover_ratio,

    -- Turnover classification
    case
        when coalesce(ai.avg_stock, 0) = 0 then 'no_stock'
        when coalesce(s.total_units_sold, 0)::numeric / nullif(ai.avg_stock, 0) > 5 then 'fast_moving'
        when coalesce(s.total_units_sold, 0)::numeric / nullif(ai.avg_stock, 0) > 2 then 'moderate'
        when coalesce(s.total_units_sold, 0)::numeric / nullif(ai.avg_stock, 0) > 0 then 'slow_moving'
        else 'dead_stock'
    end                                                    as turnover_category

from products p
left join sales s on p.product_id = s.product_id
left join avg_inventory ai on p.product_id = ai.product_id
order by turnover_ratio desc
