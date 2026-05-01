-- =============================================================
-- stg_products: Validated product catalog
-- =============================================================

with raw_products as (
    select * from {{ source('bronze', 'products') }}
)

select
    product_id,
    trim(product_name)                                   as product_name,
    category_id,
    supplier_id,
    case when unit_price > 0 then unit_price else 0 end  as unit_price,
    case when cost_price > 0 then cost_price else 0 end  as cost_price,
    -- Gross margin percentage
    case
        when unit_price > 0 and cost_price > 0
        then round(((unit_price - cost_price) / unit_price) * 100, 2)
        else 0
    end                                                  as margin_pct,
    coalesce(weight_kg, 0)                               as weight_kg,
    coalesce(is_active, true)                            as is_active,
    cast(created_at as date)                             as created_at,
    _loaded_at,
    _batch_id
from raw_products
where product_id is not null
