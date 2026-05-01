-- =============================================================
-- monthly_sales: Monthly aggregated sales with MoM growth
-- =============================================================

with monthly as (
    select
        date_trunc('month', order_date_day)::date         as sale_month,
        count(distinct order_id)                           as total_orders,
        sum(line_total_net)                                as net_revenue,
        sum(line_total_net - coalesce(line_cost, 0))       as gross_profit,
        count(distinct customer_id)                        as unique_customers,
        sum(quantity)                                       as units_sold,
        avg(line_total_net)                                as avg_order_value,
        sum(discount_amount)                               as total_discounts
    from {{ ref('fct_orders') }}
    where order_status = 'completed'
    group by 1
)

select
    sale_month,
    total_orders,
    net_revenue,
    gross_profit,
    unique_customers,
    units_sold,
    avg_order_value,
    total_discounts,

    -- Month-over-Month growth
    lag(net_revenue) over (order by sale_month)            as prev_month_revenue,
    case
        when lag(net_revenue) over (order by sale_month) > 0
        then round(
            (net_revenue - lag(net_revenue) over (order by sale_month))
            / lag(net_revenue) over (order by sale_month) * 100, 2
        )
        else null
    end                                                   as mom_growth_pct,

    -- Revenue rank
    rank() over (order by net_revenue desc)                as revenue_rank

from monthly
order by sale_month
