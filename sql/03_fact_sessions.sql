CREATE OR REPLACE VIEW `game_analytics.v_fact_sessions` AS
SELECT
    session_id,
    user_id,
    MIN(timestamp) AS start_time,
    MAX(timestamp) AS end_time,
    app_version
FROM
    `game_analytics.raw_events`
GROUP BY
    session_id, user_id, app_version;