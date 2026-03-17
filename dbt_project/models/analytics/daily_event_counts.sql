-- models/analytics/daily_event_counts.sql

WITH staging_events AS (
    SELECT * FROM {{ ref('stg_events') }}
)

SELECT
    event_date,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users
FROM staging_events
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC
