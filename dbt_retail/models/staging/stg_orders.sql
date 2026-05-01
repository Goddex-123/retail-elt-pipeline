-- =============================================================
-- stg_orders: Cleaned order headers with validation flags
-- =============================================================
-- Fixes: future-dated orders, invalid statuses

with raw_orders as (
    select * from {{ source('bronze', 'orders') }}
),

cleaned as (
    select
        order_id,
        customer_id,
        store_id,
        cast(order_date as timestamp)                    as order_date,
        cast(order_date as date)                         as order_date_day,
        lower(trim(status))                              as status,
        coalesce(total_amount, 0)                        as total_amount,
        coalesce(discount_amount, 0)                     as discount_amount,
        coalesce(shipping_cost, 0)                       as shipping_cost,
        -- Net amount after discounts
        coalesce(total_amount, 0)
            - coalesce(discount_amount, 0)
            + coalesce(shipping_cost, 0)                 as net_amount,
        -- Flag potentially invalid records
        case
            when order_date > current_timestamp then true
            else false
        end                                              as is_future_dated,
        case
            when total_amount < 0 then true
            else false
        end                                              as is_invalid_amount,
        _loaded_at,
        _batch_id
    from raw_orders
    where order_id is not null
)

select * from cleaned
where not is_future_dated  -- Exclude future-dated orders
