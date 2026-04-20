with events as (
    select
        f.event_id,
        c.category_group,
        l.geo_hash,
        l.latitude,
        l.longitude
    from {{ ref('ds_fct_events') }} f
    join {{ ref('ds_dim_category') }} c on f.category_id = c.category_id
    join {{ ref('ds_dim_location') }} l on f.location_id = l.location_id
)

select
    geo_hash,
    round(avg(latitude)::numeric, 4) as latitude,
    round(avg(longitude)::numeric, 4) as longitude,
    category_group,
    count(*) as event_count
from events
group by geo_hash, category_group
