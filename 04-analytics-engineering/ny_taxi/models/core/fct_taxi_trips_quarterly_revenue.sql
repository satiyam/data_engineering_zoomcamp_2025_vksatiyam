{{ config(materialized="table") }}

with
    trips_month_agg as (
        select
            service_type,
            extract(year from pickup_datetime) as year_var,
            extract(quarter from pickup_datetime) as quarter_var,
            extract(month from pickup_datetime) as month_var,
            sum(total_amount) as total_revenue
        from {{ ref("fact_trips") }}
        where extract(year from pickup_datetime) in (2019, 2020)
        group by 1, 2, 3, 4
        order by 1, 2, 3, 4
    ),
    quarterly_sum as (
        select
            service_type, quarter_var, year_var, sum(total_revenue) as quarterly_revenue
        from trips_month_agg
        where year_var in (2019, 2020)
        group by 1, 2, 3
        order by 1, 2, 3
    ),
    yoy as (
        select
            service_type,
            quarter_var as quarter_compared,
            year_var as curr_year,
            lead(year_var) over (
                partition by service_type, quarter_var order by year_var
            ) as next_year,
            quarterly_revenue as curryear_quarterly_revenue,
            lead(quarterly_revenue) over (
                partition by service_type, quarter_var order by year_var
            ) as nextyear_quarterly_revenue
        from quarterly_sum
        -- where year_var=2019
        order by service_type, quarter_compared, curr_year
    )
select
    *,
    100.0
    * (nextyear_quarterly_revenue - curryear_quarterly_revenue)
    / curryear_quarterly_revenue yoy_growth
from yoy
where curr_year = 2019
