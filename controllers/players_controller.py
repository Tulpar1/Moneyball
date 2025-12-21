from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models.players_model import PlayerModel
from functools import wraps
from datetime import date, datetime

players_bp = Blueprint('players', __name__, url_prefix='/players')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lütfen devam etmek için giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_age(dob):
    if not dob:
        return "-"
    if isinstance(dob, str):
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except:
            return "-"
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

@players_bp.route('/')
@login_required
def index():
    try:
        search = request.args.get('q')
        position = request.args.get('position')
        country = request.args.get('country')
        page = request.args.get('page', 1, type=int)
        
        # Sıralama parametreleri
        sort_by = request.args.get('sort_by', 'name') # Varsayılan: isim
        order = request.args.get('order', 'asc')      # Varsayılan: artan
        
        per_page = 20

        # Model'e sıralama parametrelerini de gönderiyoruz
        players_data, total_count = PlayerModel.get_all_players(
            search_query=search, 
            position_filter=position,
            country_filter=country,
            sort_by=sort_by,
            sort_order=order,
            page=page, 
            per_page=per_page
        )
        total_pages = (total_count + per_page - 1) // per_page

        for p in players_data:
            p['age'] = calculate_age(p.get('date_of_birth'))

        return render_template('players/index.html', 
                               players=players_data, 
                               page=page, 
                               total_pages=total_pages,
                               current_search=search,
                               current_pos=position,
                               current_country=country,
                               current_sort=sort_by,   # View için gerekli
                               current_order=order)    # View için gerekli
    except Exception as e:
        flash(f"Oyuncular yüklenirken bir hata oluştu: {str(e)}", 'danger')
        return render_template('players/index.html', players=[], page=1, total_pages=1)