-- =============================================================
-- stock_alerts: Low stock & out-of-stock alerts
-- =============================================================

with inventory as (
    select * from {{ ref('stg_inventory') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

stores as (
    select * from {{ ref('stg_stores') }}
)

select
    i.inventory_id,
    i.product_id,
    p.product_name,
    p.category_id,
    i.store_id,
    s.store_name,
    s.region,
    i.quantity_on_hand,
    i.reorder_level,
    i.stock_status,
    i.needs_reorder,
    i.last_restock_date,
    i.days_since_restock,

    -- Alert severity
    case
        when i.quantity_on_hand = 0 then 'critical'
        when i.quantity_on_hand <= i.reorder_level * 0.5 then 'high'
        when i.needs_reorder then 'medium'
        else 'low'
    end                                                   as alert_severity,

    -- Suggested reorder quantity (2x reorder level - current stock)
    greatest(i.reorder_level * 2 - i.quantity_on_hand, 0) as suggested_reorder_qty

from inventory i
left join products p on i.product_id = p.product_id
left join stores s on i.store_id = s.store_id
where i.needs_reorder = true or i.quantity_on_hand = 0
order by
    case
        when i.quantity_on_hand = 0 then 1
        when i.quantity_on_hand <= i.reorder_level * 0.5 then 2
        else 3
    end,
    i.days_since_restock desc
