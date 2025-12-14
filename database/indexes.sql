-- Moneyball Projesi - Performans İyileştirmeleri

-- 1. Player Valuations: Bir oyuncunun geçmiş değerlerini çekerkensorgunun tüm tabloyu taramasını engeller, direkt hedefe gitmesini sağlar.
CREATE INDEX idx_player_valuations_player_id 
ON player_valuations(player_id);

-- 2. Competitions: Ülkeye göre lig arama
CREATE INDEX idx_competitions_country 
ON competitions(country_name);

-- 3. Competitions: Lig tipine göre filtreleme için index.
CREATE INDEX idx_competitions_type 
ON competitions(type);
