CREATE OR REPLACE VIEW `game_analytics.v_dim_users` AS
SELECT
    user_id,
    MIN(DATE(timestamp)) AS install_date,
    ANY_VALUE((SELECT value FROM UNNEST(event_params) WHERE key = 'country')) AS country,
    ANY_VALUE((SELECT value FROM UNNEST(event_params) WHERE key = 'platform')) AS platform,
    ANY_VALUE((SELECT value FROM UNNEST(event_params) WHERE key = 'device_tier')) AS device_tier,
    ANY_VALUE((SELECT value FROM UNNEST(event_params) WHERE key = 'media_source')) AS media_source,
    ANY_VALUE((SELECT value FROM UNNEST(event_params) WHERE key = 'campaign_id')) AS campaign_id
FROM
    `game_analytics.raw_events`
GROUP BY
    user_id;