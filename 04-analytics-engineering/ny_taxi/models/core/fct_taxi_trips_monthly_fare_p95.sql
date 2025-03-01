{{
    config(
        materialized='table'
    )
}}

with trips as(
    select
    service_type,
    extract(year from pickup_datetime) as year_var,
    extract(month from pickup_datetime) as month_var,
    fare_amount
    from {{ ref('fact_trips') }}
    where
    1=1
    and fare_amount>0
    and trip_distance>0
    and payment_type_description in ('Cash', 'Credit card')
)
select 
    *,
    percentile_cont(fare_amount, 0.9) over(partition by service_type, year_var, month_var) as p90_fare,
    percentile_cont(fare_amount, 0.95) over(partition by service_type, year_var, month_var) as p95_fare,
    percentile_cont(fare_amount, 0.97) over(partition by service_type, year_var, month_var) as p97_fare,
    row_number() over (partition by service_type, year_var, month_var) as row_num
from trips
where year_var=2020 and month_var=4
qualify row_num=1