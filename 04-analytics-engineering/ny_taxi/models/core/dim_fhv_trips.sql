{{
    config(
        materialized='table'
    )
}}


with fhv_trips as (
    select *,
    'FHV_trips' as service_type
    from {{ ref('stg_fhv_tripdata') }}
),
dim_zones as (
    select * from {{ ref('dim_zones') }}
    where borough != 'Unknown' 
)
select 
fhv.dispatchid as dispatchid,
fhv.pickup_locationid as pickup_locationid,
dim_pu.borough as pickup_borough,
dim_pu.zone as pickup_zone,
dim_pu.service_zone as pickup_service_zone,
fhv.dropoff_locationid as dropoff_locationid,
dim_do.borough as dropoff_borough,
dim_do.zone as dropoff_zone,
dim_do.service_zone as dropoff_service_zone,
fhv.pickup_datetime as pickup_datetime,
fhv.dropoff_datetime as dropoff_datetime,
fhv.SR_Flag as SR_Flag,
fhv.dispatching_base_num as dispatching_base_num,
fhv.Affiliated_base_number as Affiliated_base_number,
fhv.service_type as service_type
from fhv_trips fhv
inner join
dim_zones dim_pu
on fhv.pickup_locationid=dim_pu.locationid
inner join
dim_zones dim_do
on fhv.dropoff_locationid=dim_do.locationid
