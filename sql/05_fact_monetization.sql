CREATE OR REPLACE VIEW `game_analytics.v_fact_monetization` AS
SELECT
    GENERATE_UUID() AS transaction_id,
    user_id,
    CAST(timestamp AS TIMESTAMP) AS timestamp,
    (SELECT value FROM UNNEST(event_params) WHERE key = 'rev_type') AS rev_type,
    (SELECT value FROM UNNEST(event_params) WHERE key = 'ad_format') AS ad_format,
    CAST((SELECT value FROM UNNEST(event_params) WHERE key = 'amount_usd') AS FLOAT64) AS amount_usd
FROM
    `game_analytics.raw_events`
WHERE
    (SELECT value FROM UNNEST(event_params) WHERE key = 'rev_type') IS NOT NULL
    AND (SELECT value FROM UNNEST(event_params) WHERE key = 'rev_type') != 'None'
    AND CAST((SELECT value FROM UNNEST(event_params) WHERE key = 'amount_usd') AS FLOAT64) > 0;