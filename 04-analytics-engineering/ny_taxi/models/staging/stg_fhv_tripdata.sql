{{
    config(
        materialized='view'
    )
}}

with tripdata as (
    select * from {{ source('staging', 'fhv_tripdata') }}
    where dispatching_base_num is not null
)
select
{{ dbt_utils.generate_surrogate_key(['dispatching_base_num', 'pickup_datetime']) }} as dispatchid,
{{ dbt.safe_cast("PUlocationID", api.Column.translate_type("integer")) }} as pickup_locationid,
{{ dbt.safe_cast("DOlocationID", api.Column.translate_type("integer")) }} as dropoff_locationid,
pickup_datetime as pickup_datetime,
dropOff_datetime as dropoff_datetime,
SR_Flag as sr_flag,
dispatching_base_num,
Affiliated_base_number as affiliated_base_number
from tripdata



