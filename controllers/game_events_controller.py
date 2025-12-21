from flask import Blueprint, render_template, request
from models.game_events_model import GameEventsModel
from datetime import datetime

game_events_bp = Blueprint('game_events', __name__)

EVENT_TYPE_MAP = {
    "Substitutions": "Oyuncu Değişikliği",
    "Goals": "Gol",
    "Shootout": "Penaltı Atışları",
    "Lineup": "Kadro"
}

def format_event_type(etype):
    return EVENT_TYPE_MAP.get(etype, etype)

def format_turkish_date(date_obj):
    if not date_obj: return ""
    aylar = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    if isinstance(date_obj, str):
        try: date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except: return date_obj
    return f"{date_obj.day} {aylar[date_obj.month]} {date_obj.year}"

@game_events_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    args = request.args.to_dict()
    
    # game_id parametresi çıkarıldı
    events = GameEventsModel.get_all_events(
        page=page, 
        per_page=per_page,
        player_name=args.get('player_name', ''),
        club_name=args.get('club_name', ''),
        event_type=args.get('event_type', ''),
        min_minute=args.get('min_minute', ''),
        max_minute=args.get('max_minute', ''),
        sort_by=args.get('sort', 'minute'),
        sort_order=args.get('order', 'asc')
    )
    
    # game_id parametresi çıkarıldı
    total_count = GameEventsModel.get_total_events_count(
        player_name=args.get('player_name', ''),
        club_name=args.get('club_name', ''),
        event_type=args.get('event_type', ''),
        min_minute=args.get('min_minute', ''),
        max_minute=args.get('max_minute', '')
    )
    
    for e in events:
        e['type_tr'] = format_event_type(e['type'])
        e['game_date_tr'] = format_turkish_date(e.get('game_date'))
        
        if e.get('description'):
            e['description'] = e['description'].lstrip(', ')
        
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template('game_events/index.html', 
                           events=events, 
                           page=page, 
                           total_pages=total_pages, 
                           filters=args)