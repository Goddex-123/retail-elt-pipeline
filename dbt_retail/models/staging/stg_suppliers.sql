-- =============================================================
-- stg_suppliers: Standardized supplier data
-- =============================================================

with raw_suppliers as (
    select * from {{ source('bronze', 'suppliers') }}
)

select
    supplier_id,
    trim(supplier_name)                                  as supplier_name,
    trim(contact_name)                                   as contact_name,
    lower(trim(contact_email))                           as contact_email,
    contact_phone,
    trim(initcap(city))                                  as city,
    coalesce(country, 'India')                           as country,
    cast(created_at as date)                             as created_at,
    _loaded_at,
    _batch_id
from raw_suppliers
where supplier_id is not null
