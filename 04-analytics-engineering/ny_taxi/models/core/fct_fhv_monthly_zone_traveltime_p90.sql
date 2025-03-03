{{
    config(
        materialized='table'
    )
}}

with dim_fhv_trips as (
    select 
    *,
    extract(year from pickup_datetime) as year_var,
    extract(month from pickup_datetime) as month_var,
    timestamp_diff(dropoff_datetime, pickup_datetime, SECOND) as trip_duration
    from {{ ref('dim_fhv_trips') }}
)
select
*,
percentile_cont(trip_duration, 0.9) over(partition by year_var, month_var, pickup_locationid, dropoff_locationid) as p90_trip_duration
from dim_fhv_trips