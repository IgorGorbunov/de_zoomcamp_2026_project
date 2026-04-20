with locations as (
    select distinct
        latitude::double precision as latitude,
        longitude::double precision as longitude
    from {{ ref('stg_strange_places') }}
    where latitude is not null
      and longitude is not null
)

select
    {{ dbt_utils.generate_surrogate_key(['latitude', 'longitude']) }} as location_id,
    latitude,
    longitude,
    -- grid cell ~20km: floor to 0.2 degree steps, concatenate as "lat:lon"
    floor(latitude / 0.2) * 0.2 || ':' || floor(longitude / 0.2) * 0.2 as geo_hash
from locations
