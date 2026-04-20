with categories as (
    select distinct category as category_name
    from {{ ref('stg_strange_places') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['category_name']) }} as category_id,
    category_name,
    case
        when category_name in ('tornadoes', 'storm_events', 'earthquakes', 'volcanoes', 'fireballs')
            then 'hazard'
        when category_name in ('caves', 'megalithic_sites', 'ghost_towns', 'thermal_springs', 'shipwrecks', 'meteorite_landings')
            then 'landmark'
        when category_name in ('ufo_sightings', 'bigfoot_sightings', 'haunted_places')
            then 'anomaly'
        else 'other'
    end as category_group,
    case
        when category_name in ('tornadoes', 'storm_events', 'thermal_springs', 'shipwrecks')
            then 'NOAA'
        when category_name in ('meteorite_landings', 'fireballs')
            then 'NASA'
        when category_name in ('earthquakes', 'volcanoes')
            then 'USGS'
        when category_name in ('caves', 'ghost_towns')
            then 'OpenStreetMap'
        when category_name = 'megalithic_sites'
            then 'Megalithic Portal'
        when category_name = 'ufo_sightings'
            then 'NUFORC'
        when category_name = 'bigfoot_sightings'
            then 'BFRO'
        when category_name = 'haunted_places'
            then 'Shadowlands Index'
        else 'Unknown'
    end as source_authority
from categories
