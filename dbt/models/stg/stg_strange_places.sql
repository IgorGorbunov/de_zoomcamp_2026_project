with source as (
    select * from {{ source('raw', 'strange_places') }}
)

select
    category,
    latitude,
    longitude,
    name,
    description,
    date,
    current_timestamp as loaded_at
from source
