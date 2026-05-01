-- =============================================================
-- revenue_by_region: Regional revenue breakdown with ranking
-- =============================================================

with regional as (
    select
        region,
        count(distinct store_id)                           as store_count,
        count(distinct order_id)                           as total_orders,
        count(distinct customer_id)                        as unique_customers,
        sum(line_total_net)                                as net_revenue,
        sum(line_total_net - coalesce(line_cost, 0))       as gross_profit,
        avg(line_total_net)                                as avg_order_value,
        sum(quantity)                                       as units_sold
    from {{ ref('fct_orders') }}
    where order_status = 'completed'
      and region is not null
    group by 1
),

total as (
    select sum(net_revenue) as grand_total from regional
)

select
    r.region,
    r.store_count,
    r.total_orders,
    r.unique_customers,
    r.net_revenue,
    r.gross_profit,
    r.avg_order_value,
    r.units_sold,
    -- Revenue share
    round(r.net_revenue / nullif(t.grand_total, 0) * 100, 2) as revenue_share_pct,
    -- Revenue per store
    round(r.net_revenue / nullif(r.store_count, 0), 2)        as revenue_per_store,
    -- Regional rank
    rank() over (order by r.net_revenue desc)                  as region_rank
from regional r
cross join total t
order by r.net_revenue desc
