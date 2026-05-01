-- =============================================================
-- refund_analysis: Return/refund trends and patterns
-- =============================================================

with returns as (
    select * from {{ ref('stg_returns') }}
),

orders as (
    select order_id, total_amount from {{ ref('stg_orders') }}
),

return_metrics as (
    select
        r.return_category,
        r.return_reason,
        r.refund_status,
        count(*)                                           as return_count,
        sum(r.refund_amount)                               as total_refund_amount,
        avg(r.refund_amount)                               as avg_refund_amount,
        count(case when r.is_refunded then 1 end)          as processed_refunds
    from returns r
    group by 1, 2, 3
),

totals as (
    select
        count(distinct order_id) as total_orders
    from orders
),

return_totals as (
    select count(distinct order_id) as total_returns from returns
)

select
    rm.return_category,
    rm.return_reason,
    rm.refund_status,
    rm.return_count,
    rm.total_refund_amount,
    rm.avg_refund_amount,
    rm.processed_refunds,

    -- Return rate (% of all orders)
    round(
        rt.total_returns::numeric / nullif(t.total_orders, 0) * 100, 2
    )                                                      as overall_return_rate_pct,

    -- % of total returns by reason
    round(
        rm.return_count::numeric / nullif(rt.total_returns, 0) * 100, 2
    )                                                      as reason_share_pct

from return_metrics rm
cross join totals t
cross join return_totals rt
order by rm.return_count desc
