-- =============================================================
-- churn_risk: Customer churn scoring based on recency
-- =============================================================

with customer_metrics as (
    select * from {{ ref('int_customer_orders') }}
)

select
    customer_id,
    customer_name,
    customer_city,
    loyalty_tier,
    total_orders,
    total_revenue,
    last_order_date,
    days_since_last_order,

    -- Churn risk level
    case
        when days_since_last_order <= 14 then 'active'
        when days_since_last_order <= 30 then 'warm'
        when days_since_last_order <= 60 then 'cooling'
        when days_since_last_order <= 90 then 'at_risk'
        else 'churned'
    end                                                   as churn_status,

    -- Churn risk score (0-100, higher = more likely to churn)
    case
        when days_since_last_order <= 14 then 10
        when days_since_last_order <= 30 then 30
        when days_since_last_order <= 60 then 55
        when days_since_last_order <= 90 then 80
        else 95
    end                                                   as churn_risk_score,

    -- Win-back priority (high-value churning customers)
    case
        when days_since_last_order > 30
            and total_revenue > (select avg(total_revenue) from customer_metrics)
        then 'high_priority'
        when days_since_last_order > 30 then 'medium_priority'
        else 'low_priority'
    end                                                   as winback_priority

from customer_metrics
order by churn_risk_score desc, total_revenue desc
