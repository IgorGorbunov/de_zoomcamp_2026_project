with events as (
    select
        f.event_id,
        c.category_name,
        c.category_group,
        l.geo_hash,
        l.latitude,
        l.longitude
    from {{ ref('ds_fct_events') }} f
    join {{ ref('ds_dim_category') }} c on f.category_id = c.category_id
    join {{ ref('ds_dim_location') }} l on f.location_id = l.location_id
)

select
    geo_hash as region,
    category_group,
    category_name,
    count(*) as event_count,
    count(case when category_group = 'hazard' then 1 end) as hazard_count,
    round(
        count(case when category_group = 'hazard' then 1 end)::numeric
        / nullif(count(*), 0) * 100, 2
    ) as risk_index
from events
group by 1, 2, 3
