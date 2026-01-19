CREATE OR REPLACE VIEW `game_analytics.v_fact_gameplay_events` AS
SELECT
    GENERATE_UUID() AS event_id,
    session_id,
    user_id,
    event_name,
    CAST((SELECT value FROM UNNEST(event_params) WHERE key = 'level_id') AS INT64) AS level_id,
    CAST((SELECT value FROM UNNEST(event_params) WHERE key = 'score') AS INT64) AS score,
    (SELECT value FROM UNNEST(event_params) WHERE key = 'fail_reason') AS fail_reason
FROM
    `game_analytics.raw_events`
WHERE
    event_name IN ('level_start', 'level_complete', 'level_fail', 'tutorial_step');