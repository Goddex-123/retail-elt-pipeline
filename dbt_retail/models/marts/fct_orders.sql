{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}

with orders as (
    select * from {{ ref('stg_orders') }}
),
customers as (
    select * from {{ ref('stg_customers') }}
)

select
    o.order_id,
    c.customer_id,
    c.city as customer_city,
    o.product_id,
    o.quantity,
    o.order_date
from orders o
left join customers c on o.customer_id = c.customer_id

{% if is_incremental() %}

  -- this filter will only be applied on an incremental run
  -- (uses >= to include records whose order_date is the same as the max order_date)
  where o.order_date > (select max(order_date) from {{ this }})

{% endif %}
