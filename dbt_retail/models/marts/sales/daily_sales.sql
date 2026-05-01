-- =============================================================
-- daily_sales: Daily aggregated sales with running totals
-- =============================================================
-- Uses window functions for running totals and moving averages

with daily as (
    select
        order_date_day                                   as sale_date,
        count(distinct order_id)                          as total_orders,
        count(order_item_id)                              as total_items,
        sum(quantity)                                      as units_sold,
        sum(line_total_gross)                              as gross_revenue,
        sum(line_total_net)                                as net_revenue,
        sum(discount_amount)                               as total_discounts,
        sum(line_total_net - coalesce(line_cost, 0))       as gross_profit,
        avg(line_total_net)                                as avg_item_value
    from {{ ref('fct_orders') }}
    where order_status = 'completed'
    group by 1
)

select
    sale_date,
    total_orders,
    total_items,
    units_sold,
    gross_revenue,
    net_revenue,
    total_discounts,
    gross_profit,
    avg_item_value,

    -- Running totals (window functions)
    sum(net_revenue) over (
        order by sale_date
        rows between unbounded preceding and current row
    )                                                    as cumulative_revenue,

    -- 7-day moving average
    avg(net_revenue) over (
        order by sale_date
        rows between 6 preceding and current row
    )                                                    as revenue_7d_ma,

    -- Day-over-day growth
    net_revenue - lag(net_revenue) over (order by sale_date)
                                                         as revenue_dod_change,
    case
        when lag(net_revenue) over (order by sale_date) > 0
        then round(
            (net_revenue - lag(net_revenue) over (order by sale_date))
            / lag(net_revenue) over (order by sale_date) * 100, 2
        )
        else null
    end                                                  as revenue_dod_growth_pct

from daily
order by sale_date
