{{
    config(
        materialized='table'
    )
}}

with shipments as (
    select * from {{ ref('stg_shipments') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

delivery_stats as (
    select
        date_trunc('month', s.shipped_date) as shipping_month,
        count(s.shipment_id) as total_shipments,
        sum(case when s.delivery_status = 'delivered' then 1 else 0 end) as on_time_deliveries,
        sum(case when s.delivery_status = 'delayed' then 1 else 0 end) as delayed_deliveries,
        sum(case when s.delivery_status = 'in_transit' then 1 else 0 end) as in_transit_deliveries,
        avg(extract(epoch from (s.actual_delivery - s.shipped_date))/86400.0) as avg_delivery_days
    from shipments s
    group by 1
)

select
    shipping_month,
    total_shipments,
    on_time_deliveries,
    delayed_deliveries,
    in_transit_deliveries,
    case when total_shipments > 0 then (on_time_deliveries::numeric / total_shipments) * 100 else 0 end as on_time_pct,
    case when total_shipments > 0 then (delayed_deliveries::numeric / total_shipments) * 100 else 0 end as delayed_pct,
    avg_delivery_days
from delivery_stats
order by shipping_month desc
