from flask import Blueprint, render_template, request
from models.player_valuations_model import PlayerValuationModel
from datetime import datetime

player_valuations_bp = Blueprint('player_valuations', __name__)

def format_turkish_date(date_obj):
    if not date_obj: return ""
    aylar = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    if isinstance(date_obj, str):
        try: date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except: return date_obj
    return f"{date_obj.day} {aylar[date_obj.month]} {date_obj.year}"

@player_valuations_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int) # Gelen sayfa numarasını alır
    per_page = 50
    args = request.args.to_dict()
    
    # Modelden verileri ve toplam sayıyı al
    valuations = PlayerValuationModel.get_all_valuations(
        page=page, per_page=per_page, 
        player_name=args.get('player_name', ''), 
        club_name=args.get('club_name', ''), 
        start_year=args.get('start_year', ''), 
        end_year=args.get('end_year', ''), 
        min_value=args.get('min_value', ''), 
        max_value=args.get('max_value', ''),
        sort_by=args.get('sort', 'date'), 
        sort_order=args.get('order', 'desc')
    )
    
    total_count = PlayerValuationModel.get_total_valuation_count(
        args.get('player_name', ''), args.get('club_name', ''), 
        args.get('start_year', ''), args.get('end_year', ''), 
        args.get('min_value', ''), args.get('max_value', '')
    )
    
    for v in valuations:
        v['date_tr'] = format_turkish_date(v['date'])
    
    total_pages = (total_count + per_page - 1) // per_page # Toplam sayfa sayısını hesaplar
    
    return render_template('player_valuations/index.html', 
                           valuations=valuations, 
                           page=page, 
                           total_pages=total_pages, 
                           filters=args)