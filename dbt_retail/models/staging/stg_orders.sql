with raw_orders as (
    select * from {{ source('bronze', 'orders') }}
)

select
    order_id,
    customer_id,
    product_id,
    -- fix negative quantities
    case 
        when quantity < 0 then 0 
        else quantity 
    end as quantity,
    cast(order_date as timestamp) as order_date
from raw_orders
