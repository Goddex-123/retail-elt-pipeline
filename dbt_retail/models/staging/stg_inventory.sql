-- =============================================================
-- stg_inventory: Stock levels with reorder flags
-- =============================================================

with raw_inventory as (
    select * from {{ source('bronze', 'inventory') }}
)

select
    inventory_id,
    product_id,
    store_id,
    coalesce(quantity_on_hand, 0)                         as quantity_on_hand,
    coalesce(reorder_level, 20)                           as reorder_level,
    cast(last_restock_date as date)                       as last_restock_date,
    cast(updated_at as timestamp)                         as updated_at,
    -- Stock status flags
    case
        when coalesce(quantity_on_hand, 0) = 0 then 'out_of_stock'
        when coalesce(quantity_on_hand, 0) <= coalesce(reorder_level, 20) then 'low_stock'
        else 'in_stock'
    end                                                  as stock_status,
    case
        when coalesce(quantity_on_hand, 0) <= coalesce(reorder_level, 20)
        then true else false
    end                                                  as needs_reorder,
    -- Days since last restock
    current_date - cast(last_restock_date as date)       as days_since_restock,
    _loaded_at,
    _batch_id
from raw_inventory
where inventory_id is not null
