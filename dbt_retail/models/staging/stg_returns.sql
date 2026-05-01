-- =============================================================
-- stg_returns: Return records with reason mapping
-- =============================================================

with raw_returns as (
    select * from {{ source('bronze', 'returns') }}
)

select
    return_id,
    order_id,
    cast(return_date as timestamp)                       as return_date,
    lower(trim(reason))                                  as return_reason,
    -- Categorize return reasons
    case
        when lower(reason) in ('defective', 'quality_issue', 'damaged_in_transit')
            then 'product_issue'
        when lower(reason) in ('wrong_item', 'size_issue')
            then 'fulfillment_error'
        when lower(reason) in ('changed_mind', 'late_delivery')
            then 'customer_preference'
        else 'other'
    end                                                  as return_category,
    case when refund_amount >= 0 then refund_amount else 0 end  as refund_amount,
    lower(trim(refund_status))                           as refund_status,
    case
        when lower(trim(refund_status)) = 'processed' then true
        else false
    end                                                  as is_refunded,
    _loaded_at,
    _batch_id
from raw_returns
where return_id is not null
