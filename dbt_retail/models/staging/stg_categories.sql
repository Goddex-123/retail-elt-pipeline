-- =============================================================
-- stg_categories: Clean category hierarchy
-- =============================================================

with raw_categories as (
    select * from {{ source('bronze', 'categories') }}
)

select
    category_id,
    trim(initcap(category_name))                         as category_name,
    parent_category_id,
    case
        when parent_category_id is null then true
        else false
    end                                                  as is_root_category,
    _loaded_at,
    _batch_id
from raw_categories
where category_id is not null
