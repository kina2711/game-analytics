CREATE OR REPLACE VIEW `game_analytics.v_dim_levels` AS
SELECT DISTINCT
    CAST((SELECT value FROM UNNEST(event_params) WHERE key = 'level_id') AS INT64) AS level_id,
    CONCAT('World 001 - Stage ', (SELECT value FROM UNNEST(event_params) WHERE key = 'level_id')) AS level_name,
    CAST((SELECT value FROM UNNEST(event_params) WHERE key = 'difficulty_index') AS FLOAT64) AS difficulty_index
FROM
    `game_analytics.raw_events`
WHERE
    (SELECT value FROM UNNEST(event_params) WHERE key = 'level_id') IS NOT NULL;