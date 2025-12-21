from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps
from datetime import datetime

# Modelleri import et
from models.games_model import GamesModel
from models.player_valuations_model import PlayerValuationModel

main_bp = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Tarih formatlayıcı (Controller içinde yardımcı fonksiyon)
def format_date_simple(date_obj):
    if not date_obj: return ""
    if isinstance(date_obj, str):
        try: date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except: return date_obj
    # Örnek: 21 Dec 2023
    return date_obj.strftime("%d %b %Y")

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # 1. Son 5 Maçı Çek (Tarihe göre azalan sıralama)
    latest_games = GamesModel.get_all_games(
        page=1, 
        per_page=5, 
        sort_by='date', 
        sort_order='DESC'
    )

    # 2. En Değerli 5 Oyuncuyu Çek (Değere göre azalan sıralama)
    top_valuations = PlayerValuationModel.get_all_valuations(
        page=1, 
        per_page=5, 
        sort_by='value', 
        sort_order='DESC'
    )

    # Verileri işle (Tarih formatı vb.)
    for game in latest_games:
        game['formatted_date'] = format_date_simple(game['date'])
    
    for val in top_valuations:
        val['formatted_date'] = format_date_simple(val['date'])

    return render_template('main/dashboard.html', 
                           games=latest_games, 
                           valuations=top_valuations)