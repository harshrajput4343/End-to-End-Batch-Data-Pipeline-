-- models/staging/stg_events.sql

WITH raw_data AS (
    SELECT * FROM {{ source('raw_data', 'events') }}
)

SELECT
    user_id::INT as user_id,
    event_type::VARCHAR as event_type,
    "timestamp"::TIMESTAMP as event_timestamp,
    "timestamp"::DATE as event_date
FROM raw_data
WHERE user_id IS NOT NULL 
  AND event_type IS NOT NULL
