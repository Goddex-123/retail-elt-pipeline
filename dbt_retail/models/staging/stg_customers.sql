with raw_customers as (
    select * from {{ source('bronze', 'customers') }}
)

select distinct
    customer_id,
    trim(name) as name,
    case 
        when city is null then 'Unknown'
        else trim(initcap(city))
    end as city,
    cast(signup_date as date) as signup_date
from raw_customers
