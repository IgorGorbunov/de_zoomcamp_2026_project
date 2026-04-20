with events as (
    select
        category,
        latitude::double precision as latitude,
        longitude::double precision as longitude,
        name as event_name,
        description as event_description,
        date
    from {{ ref('stg_strange_places') }}
),

dim_category as (
    select * from {{ ref('ds_dim_category') }}
),

dim_location as (
    select * from {{ ref('ds_dim_location') }}
),

dim_date as (
    select * from {{ ref('ds_dim_date') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['e.category', 'e.latitude', 'e.longitude', 'e.event_name', 'e.date']) }} as event_id,
    c.category_id,
    l.location_id,
    d.date_id,
    e.event_name,
    e.event_description
from events e
left join dim_category c
    on e.category = c.category_name
left join dim_location l
    on e.latitude = l.latitude
    and e.longitude = l.longitude
left join dim_date d
    on cast(e.date as date) = d.full_date
