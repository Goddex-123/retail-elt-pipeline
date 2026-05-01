-- =============================================================
-- stg_payments: Standardized payment transactions
-- =============================================================

with raw_payments as (
    select * from {{ source('bronze', 'payments') }}
)

select
    payment_id,
    order_id,
    lower(trim(payment_method))                          as payment_method,
    lower(trim(payment_status))                          as payment_status,
    cast(payment_date as timestamp)                      as payment_date,
    case when amount >= 0 then amount else 0 end         as amount,
    coalesce(upper(trim(currency)), 'INR')               as currency,
    -- Payment success flag for easy filtering
    case
        when lower(trim(payment_status)) = 'success' then true
        else false
    end                                                  as is_successful,
    _loaded_at,
    _batch_id
from raw_payments
where payment_id is not null
