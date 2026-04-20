with events as (
    select
        f.event_id,
        c.category_name,
        c.category_group,
        d.year,
        d.month,
        d.season
    from {{ ref('ds_fct_events') }} f
    join {{ ref('ds_dim_category') }} c on f.category_id = c.category_id
    join {{ ref('ds_dim_date') }} d on f.date_id = d.date_id
    where d.year is not null
),

yearly as (
    select
        year,
        month,
        season,
        category_name,
        category_group,
        count(*) as event_count
    from events
    group by 1, 2, 3, 4, 5
),

with_yoy as (
    select
        *,
        lag(event_count) over (
            partition by month, category_name
            order by year
        ) as prev_year_count
    from yearly
)

select
    year,
    month,
    season,
    category_name,
    category_group,
    event_count,
    round(
        (event_count - prev_year_count)::numeric
        / nullif(prev_year_count, 0) * 100, 2
    ) as yoy_change_pct
from with_yoy
