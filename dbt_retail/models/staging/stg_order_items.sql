-- =============================================================
-- stg_order_items: Order line items with calculated fields
-- =============================================================

with raw_order_items as (
    select * from {{ source('bronze', 'order_items') }}
)

select
    order_item_id,
    order_id,
    product_id,
    -- Fix negative quantities
    case when quantity < 0 then 0 else quantity end      as quantity,
    unit_price,
    coalesce(discount_pct, 0)                            as discount_pct,
    -- Line total before discount
    case when quantity < 0 then 0 else quantity end
        * unit_price                                     as line_total_gross,
    -- Line total after discount
    case when quantity < 0 then 0 else quantity end
        * unit_price
        * (1 - coalesce(discount_pct, 0) / 100.0)       as line_total_net,
    -- Discount amount
    case when quantity < 0 then 0 else quantity end
        * unit_price
        * (coalesce(discount_pct, 0) / 100.0)            as discount_amount,
    _loaded_at,
    _batch_id
from raw_order_items
where order_item_id is not null
