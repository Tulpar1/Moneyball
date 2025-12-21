from flask import Flask, redirect, url_for
from database import Config

# --- Controller Importları ---
from controllers.auth_controller import auth_bp
from controllers.main_controller import main_bp
from controllers.players_controller import players_bp
from controllers.clubs_controller import clubs_bp
from controllers.competitions_controller import competitions_bp
from controllers.games_controller import games_bp
from controllers.appearances_controller import appearances_bp
from controllers.game_events_controller import game_events_bp
from controllers.player_valuations_controller import player_valuations_bp
from controllers.club_games_controller import club_games_bp
from controllers.admin_controller import admin_bp # Mutlaka ekli olmalı

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'moneyball_gizli_anahtar_123'

# --- Blueprint Kayıtları ---
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp) # HATA ÇÖZÜMÜ: BuildError'u engeller

# Veri Modülleri
app.register_blueprint(players_bp, url_prefix='/players')
app.register_blueprint(clubs_bp, url_prefix='/clubs')
app.register_blueprint(competitions_bp, url_prefix='/competitions')
app.register_blueprint(games_bp, url_prefix='/games')
app.register_blueprint(appearances_bp, url_prefix='/appearances')
app.register_blueprint(game_events_bp, url_prefix='/game_events')
app.register_blueprint(player_valuations_bp, url_prefix='/player_valuations')
app.register_blueprint(club_games_bp, url_prefix='/club_games')

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('main.dashboard'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)