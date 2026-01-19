-- Khởi tạo Dataset
CREATE SCHEMA IF NOT EXISTS `game_analytics`;

-- Tạo bảng Staging để chứa dữ liệu nested JSON
CREATE OR REPLACE TABLE `game_analytics.raw_events` (
    user_id STRING,
    session_id STRING,
    timestamp TIMESTAMP,
    event_name STRING,
    app_version STRING,
    event_params ARRAY<STRUCT<key STRING, value STRING>>
);