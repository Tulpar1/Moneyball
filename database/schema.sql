-- File: database/schema.sql
-- Author: Hasan Özgür Çağan
-- Description: SQL schema for the "Players" table in the Moneyball project.
--              Defines all relational attributes used by the Flask backend model.
--              Each column corresponds directly to attributes in the Players Python class.

------------------------------------------------------------
-- TABLE: Players
-- Purpose: Store all player-related data, including personal
--          information, career stats, and market values.
------------------------------------------------------------

CREATE TABLE Players (
    player_id INTEGER PRIMARY KEY,                    -- Unique identifier for each player
    first_name VARCHAR(255),                          -- Player's first name
    last_name VARCHAR(255),                           -- Player's last name
    name VARCHAR(255),                                -- Full display name
    last_season INTEGER,                              -- Last active season
    current_club_id INTEGER,                          -- Current club ID (foreign key reference)
    player_code VARCHAR(255),                         -- Unique player code used by Transfermarkt
    country_of_birth VARCHAR(255),                    -- Country where player was born
    city_of_birth VARCHAR(255),                       -- City where player was born
    country_of_citizenship VARCHAR(255),              -- Citizenship (nationality)
    date_of_birth DATE,                               -- Birth date
    sub_position VARCHAR(255),                        -- Detailed field position (e.g. Left-Back)
    position VARCHAR(255),                            -- General position (e.g. Defender, Midfield)
    foot VARCHAR(50),                                 -- Dominant foot (Left, Right, Both)
    height_in_cm INTEGER,                             -- Height in centimeters
    market_value_in_eur BIGINT,                       -- Current market value (in Euros)
    highest_market_value_in_eur BIGINT,               -- Peak market value (in Euros)
    contract_expiration_date DATE,                    -- Contract end date (if available)
    agent_name VARCHAR(255),                          -- Player's agent or management company
    image_url TEXT,                                   -- URL to player's image
    url TEXT,                                         -- Profile URL (e.g. Transfermarkt page)
    current_club_domestic_competition_id VARCHAR(50), -- League/competition ID (e.g. GB1, TR1)
    current_club_name VARCHAR(255)                    -- Name of current club
);
