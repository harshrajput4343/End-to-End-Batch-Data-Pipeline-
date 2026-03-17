-- models/staging/stg_events.sql

WITH raw_data AS (
    SELECT * FROM {{ source('raw_data', 'events') }}
)

SELECT
    CAST(user_id AS INT64) as user_id,
    CAST(event_type AS STRING) as event_type,
    CAST(timestamp AS TIMESTAMP) as event_timestamp,
    EXTRACT(DATE FROM timestamp) as event_date
FROM raw_data
WHERE user_id IS NOT NULL 
  AND event_type IS NOT NULL
