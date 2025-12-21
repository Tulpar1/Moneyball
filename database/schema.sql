-- File: database/schema.sql
-- Author: Hasan Özgür Çağan
-- Description: SQL schema for the "Players" table in the Moneyball project.
--              Defines all relational attributes used by the Flask backend model.
--              Each column corresponds directly to attributes in the Players Python class.


-- TABLE: Players
-- Purpose: Store all player-related data, including personal
--          information, career stats, and market values.


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

-- =========================================
-- TABLE: Competitions
-- =========================================
CREATE TABLE IF NOT EXISTS Competitions (
    competition_id        VARCHAR(16) PRIMARY KEY,  -- ör: GB1, CL, IT1 (harf/rakam)
    competition_code      VARCHAR(64),             -- slug: premier-league, cl, ...
    name                  VARCHAR(128),            -- display name
    sub_type              VARCHAR(64),             -- first_tier | domestic_cup | domestic_super_cup | ...
    type                  VARCHAR(64),             -- domestic_league | international_cup | other
    country_id            INTEGER,                 -- -1 ise uluslararası
    country_name          VARCHAR(64),
    domestic_league_code  VARCHAR(16),             -- ör: GB1, ES1
    confederation         VARCHAR(32),             -- UEFA, CONMEBOL, europa (csv’de böyle geçiyor)
    url                   TEXT
);

-- =========================================
-- TABLE: PlayerValuations
-- Purpose: Historical market values (time series) per player.
-- PK: (player_id, date)
-- =========================================
CREATE TABLE IF NOT EXISTS PlayerValuations (
    player_id                             INTEGER      NOT NULL,
    last_season                           INTEGER,
    datetime                              TIMESTAMP,   -- e.g. 2003-12-09 00:00:00
    date                                  DATE         NOT NULL,  -- e.g. 2003-12-09
    dateweek                              DATE,        -- start-of-week date if provided
    market_value_in_eur                   BIGINT,
    n                                     INTEGER,     -- sequence/index in original source
    current_club_id                       INTEGER,
    player_club_domestic_competition_id   VARCHAR(16), -- e.g. TR1, GB1, IT1
    PRIMARY KEY (player_id, date)
    -- FOREIGN KEY (player_id) REFERENCES Players(player_id)
    -- FOREIGN KEY (current_club_id) REFERENCES Clubs(club_id)
);

CREATE TABLE IF NOT EXISTS Appearances (
    appearance_id VARCHAR(255) PRIMARY KEY,
    game_id INTEGER,
    player_id INTEGER,
    player_club_id INTEGER,
    player_current_club_id INTEGER,
    date DATE,
    player_name VARCHAR(255),
    competition_id VARCHAR(16),
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    minutes_played INTEGER DEFAULT 0

    -- FOREIGN KEY (player_id) REFERENCES Players(player_id),
    -- FOREIGN KEY (competition_id) REFERENCES Competitions(competition_id)
);
-- =========================================
-- TABLE: Clubs
-- =========================================
CREATE TABLE IF NOT EXISTS Clubs (
    club_id INTEGER PRIMARY KEY,
    club_code VARCHAR(255),
    name VARCHAR(255),
    domestic_competition_id VARCHAR(16),
    total_market_value BIGINT,
    squad_size INTEGER,
    average_age FLOAT,
    foreigners_number INTEGER,
    foreigners_percentage FLOAT,
    national_team_players INTEGER,
    stadium_name VARCHAR(255),
    stadium_seats INTEGER,
    net_transfer_record VARCHAR(255),
    coach_name VARCHAR(255),
    last_season INTEGER,
    url TEXT
);

-- =========================================
-- TABLE: ClubGames
-- AMAC: Kulüplerin maç istatistiklerini tutar.
-- CASCADE: Kulüp silinirse, ona ait maç kayıtları da silinir 
-- =========================================
CREATE TABLE IF NOT EXISTS ClubGames (
    game_id INTEGER,
    club_id INTEGER,
    own_goals INTEGER,
    own_position INTEGER,
    own_manager_name VARCHAR(255),
    opponent_id INTEGER,
    opponent_goals INTEGER,
    opponent_position INTEGER,
    opponent_manager_name VARCHAR(255),
    hosting VARCHAR(10),
    is_win INTEGER,
    
    -- Bir maçta aynı kulüp sadece bir kez geçebilir
    PRIMARY KEY (game_id, club_id),
    
    -- CASCADE BAĞLANTISI BURADA:
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id) ON DELETE CASCADE
);