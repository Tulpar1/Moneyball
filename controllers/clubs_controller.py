from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from models.clubs_model import ClubModel
from functools import wraps

clubs_bp = Blueprint('clubs', __name__, url_prefix='/clubs')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@clubs_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtreleri al
    args = request.args
    search = args.get('q', '')
    league = args.get('league', '')
    min_squad = args.get('min_squad', '')
    max_squad = args.get('max_squad', '')
    sort_by = args.get('sort', 'name')
    sort_order = args.get('order', 'asc')

    clubs, total_count = ClubModel.get_all_clubs(
        search_query=search, 
        league_filter=league,
        min_squad=min_squad,
        max_squad=max_squad,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page, 
        per_page=per_page
    )
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template('clubs/index.html', 
                           clubs=clubs, 
                           page=page, 
                           total_pages=total_pages,
                           filters=args,
                           total_count=total_count)

@clubs_bp.route('/get/<int:club_id>')
@login_required
def get_club(club_id):
    club = ClubModel.get_club_by_id(club_id)
    return jsonify(club) if club else (jsonify({'error': 'Not found'}), 404)

@clubs_bp.route('/add', methods=['POST'])
@login_required
def add_club():
    try:
        ClubModel.add_club(
            name=request.form['name'],
            competition_id=request.form['domestic_competition_id'],
            squad_size=request.form['squad_size'],
            image_url=request.form.get('image_url', ''),
            url=request.form.get('url', '')
        )
        flash('Kulüp başarıyla eklendi.', 'success')
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'danger')
    return redirect(url_for('clubs.index'))

@clubs_bp.route('/update/<int:club_id>', methods=['POST'])
@login_required
def update_club(club_id):
    try:
        ClubModel.update_club(
            club_id=club_id,
            name=request.form['name'],
            competition_id=request.form['domestic_competition_id'],
            squad_size=request.form['squad_size'],
            image_url=request.form.get('image_url', ''),
            url=request.form.get('url', '')
        )
        flash('Kulüp güncellendi.', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
    return redirect(url_for('clubs.index'))

@clubs_bp.route('/delete/<int:club_id>', methods=['POST'])
@login_required
def delete_club(club_id):
    # Güvenlik Kontrolü: Sadece admin silebilir
    if session.get('role') != 'admin':
        flash('Bu işlem için yetkiniz yok!', 'danger')
        return redirect(url_for('clubs.index'))

    if ClubModel.delete_club(club_id):
        flash('Kulüp başarıyla silindi.', 'success')
    else:
        flash('Kulüp silinirken hata oluştu (Bağlı veriler olabilir).', 'danger')
        
    return redirect(url_for('clubs.index'))