from flask import Blueprint, render_template, request
from models.games_model import GamesModel
from datetime import datetime

games_bp = Blueprint('games', __name__)

# Tür çevirisi için sözlük
COMPETITION_TYPE_MAP = {
    "domestic_cup": "Ulusal Kupa",
    "domestic_league": "Lig",
    "international_cup": "Uluslararası Kupa",
    "other": "Diğer"
}

def format_turkish_date(date_obj):
    if not date_obj: return ""
    aylar = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    if isinstance(date_obj, str):
        try: date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except: return date_obj
    return f"{date_obj.day} {aylar[date_obj.month]} {date_obj.year}"

def format_competition_type(ctype):
    # Eğer listede varsa Türkçesini, yoksa orijinalini döndür
    return COMPETITION_TYPE_MAP.get(ctype, ctype)

@games_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    args = request.args.to_dict()
    
    # Modelden verileri çek (Yeni 'opponent' parametresi eklendi)
    games = GamesModel.get_all_games(
        page=page, 
        per_page=per_page,
        search_term=args.get('search_term', ''),
        opponent=args.get('opponent', ''), # Yeni rakip filtresi
        competition_id=args.get('competition_id', ''),
        season=args.get('season', ''),
        min_attendance=args.get('min_attendance', ''),
        max_attendance=args.get('max_attendance', ''),
        competition_type=args.get('competition_type', ''),
        sort_by=args.get('sort', 'date'),
        sort_order=args.get('order', 'desc')
    )
    
    # Sayfalama için toplam sayıyı çek
    total_count = GamesModel.get_total_games_count(
        search_term=args.get('search_term', ''),
        opponent=args.get('opponent', ''), # Yeni rakip filtresi
        competition_id=args.get('competition_id', ''),
        season=args.get('season', ''),
        min_attendance=args.get('min_attendance', ''),
        max_attendance=args.get('max_attendance', ''),
        competition_type=args.get('competition_type', '')
    )
    
    # Verileri işle (Tarih formatı ve Tür çevirisi)
    for g in games:
        g['date_tr'] = format_turkish_date(g['date'])
        g['type_tr'] = format_competition_type(g['competition_type'])
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template('games/index.html', 
                           games=games, 
                           page=page, 
                           total_pages=total_pages, 
                           filters=args)