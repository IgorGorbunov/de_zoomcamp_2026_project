with dates as (
    select distinct
        cast(date as date) as full_date
    from {{ ref('stg_strange_places') }}
    where date is not null
      and date != ''
      and date ~ '^\d{4}-\d{2}-\d{2}$'
      and cast(left(date, 4) as int) between 1000 and 2100
)

select
    {{ dbt_utils.generate_surrogate_key(['full_date']) }} as date_id,
    full_date,
    extract(year from full_date) as year,
    extract(month from full_date) as month,
    extract(day from full_date) as day,
    extract(quarter from full_date) as quarter,
    extract(dow from full_date) as day_of_week,
    case
        when extract(month from full_date) in (12, 1, 2) then 'winter'
        when extract(month from full_date) in (3, 4, 5) then 'spring'
        when extract(month from full_date) in (6, 7, 8) then 'summer'
        when extract(month from full_date) in (9, 10, 11) then 'autumn'
    end as season
from dates
