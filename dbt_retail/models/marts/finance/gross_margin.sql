-- =============================================================
-- gross_margin: Product & category margin analysis
-- =============================================================

with product_margins as (
    select
        product_id,
        product_name,
        category_id,
        sum(line_total_net)                                as total_revenue,
        sum(coalesce(line_cost, 0))                        as total_cost,
        sum(line_total_net - coalesce(line_cost, 0))       as gross_profit,
        sum(quantity)                                       as total_units
    from {{ ref('fct_orders') }}
    where order_status = 'completed'
    group by 1, 2, 3
)

select
    product_id,
    product_name,
    category_id,
    total_revenue,
    total_cost,
    gross_profit,
    total_units,

    -- Gross margin percentage
    case
        when total_revenue > 0
        then round(cast((gross_profit / total_revenue) * 100 as numeric), 2)
        else 0
    end                                                    as gross_margin_pct,

    -- Profit per unit
    case
        when total_units > 0
        then round(cast(gross_profit / total_units as numeric), 2)
        else 0
    end                                                    as profit_per_unit,

    -- Margin tier
    case
        when total_revenue = 0 then 'no_sales'
        when gross_profit / nullif(total_revenue, 0) >= 0.5 then 'high_margin'
        when gross_profit / nullif(total_revenue, 0) >= 0.25 then 'medium_margin'
        when gross_profit / nullif(total_revenue, 0) >= 0 then 'low_margin'
        else 'negative_margin'
    end                                                    as margin_tier

from product_margins
order by gross_profit desc