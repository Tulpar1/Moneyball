-- Moneyball/database/cleanup.sql
SET SQL_SAFE_UPDATES = 0;
DELETE FROM clubs 
WHERE name IS NULL OR name = '';
-- B) Rakibi belli olmayan (NULL) maçları sil
DELETE FROM club_games 
WHERE opponent_id IS NULL;
-- C) Rakibi veritabanında olmayan (Hayalet) maçları sil
DELETE FROM club_games 
WHERE opponent_id NOT IN (SELECT club_id FROM clubs);
SET SQL_SAFE_UPDATES = 1;