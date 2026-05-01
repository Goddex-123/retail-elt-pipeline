-- =============================================================
-- stg_shipments: Delivery tracking with performance metrics
-- =============================================================

with raw_shipments as (
    select * from {{ source('bronze', 'shipments') }}
)

select
    shipment_id,
    order_id,
    trim(carrier)                                        as carrier,
    upper(trim(tracking_number))                         as tracking_number,
    cast(shipped_date as timestamp)                      as shipped_date,
    cast(estimated_delivery as timestamp)                as estimated_delivery,
    cast(actual_delivery as timestamp)                   as actual_delivery,
    lower(trim(status))                                  as delivery_status,
    -- Delivery time in days
    case
        when actual_delivery is not null and shipped_date is not null
        then extract(day from (actual_delivery - shipped_date))
        else null
    end                                                  as delivery_days,
    -- Was it delivered on time?
    case
        when actual_delivery is not null and estimated_delivery is not null
        then actual_delivery <= estimated_delivery
        else null
    end                                                  as is_on_time,
    -- Days late (negative = early)
    case
        when actual_delivery is not null and estimated_delivery is not null
        then extract(day from (actual_delivery - estimated_delivery))
        else null
    end                                                  as days_variance,
    _loaded_at,
    _batch_id
from raw_shipments
where shipment_id is not null
