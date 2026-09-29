{{
    config(
        materialized='table'
    )
}}

with promotions as (
    select * from {{ ref('stg_promotions') }}
),

orders as (
    select * from {{ ref('fct_orders') }}
)

select
    p.promotion_id,
    p.promotion_name,
    p.discount_type,
    p.discount_value,
    p.is_currently_active,
    count(distinct o.order_id) as promoted_orders,
    count(distinct o.customer_id) as unique_customers,
    sum(o.quantity) as units_sold,
    sum(o.line_total_net) as net_revenue,
    sum(o.discount_amount) as total_discount_given,
    sum(o.gross_profit) as total_profit
from promotions p
left join orders o 
    on o.order_date >= p.start_date 
    and o.order_date <= p.end_date
    and o.line_total_gross >= p.min_order_value
group by 1, 2, 3, 4, 5
