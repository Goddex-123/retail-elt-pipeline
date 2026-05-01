-- =============================================================
-- payment_success_rate: Payment method performance analysis
-- =============================================================

with payments as (
    select * from {{ ref('stg_payments') }}
),

method_metrics as (
    select
        payment_method,
        count(*)                                           as total_transactions,
        count(case when is_successful then 1 end)          as successful_transactions,
        count(case when payment_status = 'failed' then 1 end)   as failed_transactions,
        count(case when payment_status = 'pending' then 1 end)  as pending_transactions,
        count(case when payment_status = 'refunded' then 1 end) as refunded_transactions,
        sum(case when is_successful then amount else 0 end)     as successful_volume,
        sum(amount)                                        as total_volume,
        avg(case when is_successful then amount else null end)  as avg_successful_amount
    from payments
    group by 1
),

total as (
    select sum(total_transactions) as grand_total from method_metrics
)

select
    mm.payment_method,
    mm.total_transactions,
    mm.successful_transactions,
    mm.failed_transactions,
    mm.pending_transactions,
    mm.refunded_transactions,
    mm.successful_volume,
    mm.total_volume,
    mm.avg_successful_amount,

    -- Success rate
    round(
        mm.successful_transactions::numeric / nullif(mm.total_transactions, 0) * 100, 2
    )                                                      as success_rate_pct,

    -- Failure rate
    round(
        mm.failed_transactions::numeric / nullif(mm.total_transactions, 0) * 100, 2
    )                                                      as failure_rate_pct,

    -- Market share
    round(
        mm.total_transactions::numeric / nullif(t.grand_total, 0) * 100, 2
    )                                                      as market_share_pct,

    -- Reliability tier
    case
        when mm.successful_transactions::numeric / nullif(mm.total_transactions, 0) >= 0.95
            then 'excellent'
        when mm.successful_transactions::numeric / nullif(mm.total_transactions, 0) >= 0.90
            then 'good'
        when mm.successful_transactions::numeric / nullif(mm.total_transactions, 0) >= 0.80
            then 'fair'
        else 'poor'
    end                                                    as reliability_tier

from method_metrics mm
cross join total t
order by mm.total_transactions desc
