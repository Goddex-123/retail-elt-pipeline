-- =============================================================
-- customer_lifetime_value: CLV with RFM scoring
-- =============================================================
-- Recency / Frequency / Monetary analysis for customer segmentation

with customer_metrics as (
    select * from {{ ref('int_customer_orders') }}
),

rfm as (
    select
        customer_id,
        customer_name,
        customer_city,
        loyalty_tier,
        age_group,
        total_orders,
        total_revenue,
        avg_order_value,
        first_order_date,
        last_order_date,
        unique_products_bought,
        total_items_bought,
        days_since_last_order,

        -- RFM Scoring (1-5, where 5 is best)
        ntile(5) over (order by days_since_last_order desc)   as recency_score,
        ntile(5) over (order by total_orders)                  as frequency_score,
        ntile(5) over (order by total_revenue)                 as monetary_score

    from customer_metrics
    where total_orders > 0
)

select
    *,
    -- Combined RFM score
    recency_score + frequency_score + monetary_score      as rfm_score,

    -- Customer segment
    case
        when recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4
            then 'Champions'
        when recency_score >= 3 and frequency_score >= 3
            then 'Loyal Customers'
        when recency_score >= 4 and frequency_score <= 2
            then 'New Customers'
        when recency_score <= 2 and frequency_score >= 3
            then 'At Risk'
        when recency_score <= 2 and frequency_score <= 2
            then 'Hibernating'
        else 'Potential Loyalist'
    end                                                   as customer_segment,

    -- Estimated CLV (simplified: avg_order_value * frequency * projected_lifespan)
    round(avg_order_value * total_orders * 2.5, 2)        as estimated_clv

from rfm
order by estimated_clv desc
