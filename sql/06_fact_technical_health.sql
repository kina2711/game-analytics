CREATE OR REPLACE VIEW `game_analytics.v_fact_technical_health` AS
SELECT
    GENERATE_UUID() AS log_id,
    user_id,
    CAST((SELECT value FROM UNNEST(event_params) WHERE key = 'fps_avg') AS INT64) AS fps_avg,
    CAST((SELECT value FROM UNNEST(event_params) WHERE key = 'memory_usage_mb') AS INT64) AS memory_usage_mb,
    CAST((SELECT value FROM UNNEST(event_params) WHERE key = 'is_crash') AS INT64) AS is_crash
FROM
    `game_analytics.raw_events`
WHERE
    (SELECT value FROM UNNEST(event_params) WHERE key = 'fps_avg') IS NOT NULL;