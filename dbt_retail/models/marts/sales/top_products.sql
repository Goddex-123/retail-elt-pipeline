-- =============================================================
-- top_products: Product performance with rank & contribution %
-- =============================================================

with product_perf as (
    select
        product_id,
        product_name,
        category_id,
        count(distinct order_id)                           as order_count,
        sum(quantity)                                       as total_units,
        sum(line_total_net)                                as total_revenue,
        sum(line_total_net - coalesce(line_cost, 0))       as total_profit,
        avg(line_total_net)                                as avg_revenue_per_order,
        count(distinct customer_id)                        as unique_buyers,
        avg(product_margin_pct)                            as avg_margin_pct
    from {{ ref('fct_orders') }}
    where order_status = 'completed'
    group by 1, 2, 3
),

total as (
    select sum(total_revenue) as grand_total from product_perf
)

select
    pp.product_id,
    pp.product_name,
    pp.category_id,
    pp.order_count,
    pp.total_units,
    pp.total_revenue,
    pp.total_profit,
    pp.avg_revenue_per_order,
    pp.unique_buyers,
    pp.avg_margin_pct,

    -- Contribution %
    round(cast(pp.total_revenue / nullif(t.grand_total, 0) * 100 as numeric), 2) as revenue_contribution_pct,

    -- Cumulative contribution (Pareto)
    round(cast(
        sum(pp.total_revenue) over (order by pp.total_revenue desc)
        / nullif(t.grand_total, 0) * 100 as numeric), 2
    )                                                          as cumulative_contribution_pct,

    -- Product rank
    rank() over (order by pp.total_revenue desc)               as product_rank,
    dense_rank() over (order by pp.total_units desc)           as units_rank

from product_perf pp
cross join total t
order by pp.total_revenue desc