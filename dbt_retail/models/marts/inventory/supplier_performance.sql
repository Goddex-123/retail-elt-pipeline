{{
    config(
        materialized='table'
    )
}}

with suppliers as (
    select * from {{ ref('stg_suppliers') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

inventory as (
    select * from {{ ref('stg_inventory') }}
)

select
    s.supplier_id,
    s.supplier_name,
    s.city as supplier_city,
    count(distinct p.product_id) as total_products_supplied,
    coalesce(sum(i.quantity_on_hand), 0) as total_units_in_stock
from suppliers s
left join products p on s.supplier_id = p.supplier_id
left join inventory i on p.product_id = i.product_id
group by 1, 2, 3
