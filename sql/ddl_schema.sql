-- ============================================================
-- MASTER DDL SCHEMA - MOBILE GAME ANALYTICS
-- AUTHOR: Rabbit
-- ============================================================

-- 1. Create Schema
CREATE SCHEMA IF NOT EXISTS `game_analytics`;

-- 2. Create Dimensions
-- [Execute content of 01_dim_users.sql]
-- [Execute content of 02_dim_levels.sql]

-- 3. Create Facts
-- [Execute content of 03_fact_sessions.sql]
-- [Execute content of 04_fact_gameplay_events.sql]
-- [Execute content of 05_fact_monetization.sql]
-- [Execute content of 06_fact_technical_health.sql]

SELECT 'Warehouse Schema Deployed Successfully' AS status;