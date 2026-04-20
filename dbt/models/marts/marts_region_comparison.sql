with events as (
    select
        f.event_id,
        c.category_group,
        l.geo_hash as region
    from {{ ref('ds_fct_events') }} f
    join {{ ref('ds_dim_category') }} c on f.category_id = c.category_id
    join {{ ref('ds_dim_location') }} l on f.location_id = l.location_id
)

select
    region,
    count(*) as total_count,
    count(case when category_group = 'hazard' then 1 end) as hazard_count,
    count(case when category_group = 'landmark' then 1 end) as landmark_count,
    count(case when category_group = 'anomaly' then 1 end) as anomaly_count,
    round(
        count(case when category_group = 'hazard' then 1 end)::numeric
        / nullif(count(*), 0) * 100, 2
    ) as risk_index,
    round(
        count(case when category_group = 'landmark' then 1 end)::numeric
        / nullif(count(*), 0) * 100, 2
    ) as tourism_index
from events
group by region
