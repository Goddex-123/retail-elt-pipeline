-- =============================================================
-- repeat_customer_rate: Cohort-based repeat purchase analysis
-- =============================================================

with customer_orders as (
    select * from {{ ref('int_customer_orders') }}
),

cohort_data as (
    select
        date_trunc('month', first_order_date)::date       as signup_cohort,
        count(distinct customer_id)                        as total_customers,
        count(distinct case when total_orders >= 2 then customer_id end)
                                                           as repeat_customers,
        count(distinct case when total_orders >= 3 then customer_id end)
                                                           as frequent_customers,
        avg(total_orders)                                  as avg_orders_per_customer,
        avg(total_revenue)                                 as avg_revenue_per_customer
    from customer_orders
    group by 1
)

select
    signup_cohort,
    total_customers,
    repeat_customers,
    frequent_customers,
    avg_orders_per_customer,
    avg_revenue_per_customer,

    -- Repeat rate
    round(repeat_customers::numeric / nullif(total_customers, 0) * 100, 2)
                                                           as repeat_rate_pct,
    -- Frequent buyer rate
    round(frequent_customers::numeric / nullif(total_customers, 0) * 100, 2)
                                                           as frequent_rate_pct
from cohort_data
order by signup_cohort
