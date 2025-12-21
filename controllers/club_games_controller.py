from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from models.club_games_model import ClubGameModel
from models.clubs_model import ClubModel
from functools import wraps

club_games_bp = Blueprint('club_games', __name__, url_prefix='/club_games')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@club_games_bp.route('/')
@login_required
def index():
    try:
        search = request.args.get('q')
        win_status = request.args.get('is_win')
        page = request.args.get('page', 1, type=int)
        per_page = 20

        stats, total_count = ClubGameModel.get_all_club_games(search, win_status, page, per_page)
        all_clubs, _ = ClubModel.get_all_clubs(per_page=1000) # Dropdown için

        total_pages = (total_count + per_page - 1) // per_page if total_count else 1

        return render_template('club_games/index.html', 
                               stats=stats, 
                               page=page, 
                               total_pages=total_pages,
                               total_count=total_count,
                               current_search=search,
                               current_win=win_status,
                               clubs=all_clubs)
    except Exception as e:
        print(f"HATA: {e}")
        return render_template('club_games/index.html', stats=[], page=1, total_pages=1, total_count=0, clubs=[])

@club_games_bp.route('/add', methods=['POST'])
@login_required
def add_match():
    if session.get('role') != 'admin':
        flash('Yetkiniz yok.', 'danger')
        return redirect(url_for('club_games.index'))
        
    try:
        ClubGameModel.add_match(
            date=request.form['date'],
            home_club_id=request.form['home_club_id'],
            away_club_id=request.form['away_club_id'],
            home_score=request.form['home_score'],
            away_score=request.form['away_score'],
            home_manager=request.form.get('home_manager'),
            away_manager=request.form.get('away_manager')
        )
        flash('Maç eklendi.', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
    return redirect(url_for('club_games.index'))

@club_games_bp.route('/delete/<int:game_id>', methods=['POST'])
@login_required
def delete_match(game_id):
    if session.get('role') != 'admin':
        flash('Yetkiniz yok.', 'danger')
        return redirect(url_for('club_games.index'))

    if ClubGameModel.delete_match(game_id):
        flash('Maç başarıyla silindi.', 'success')
    else:
        flash('Silme işleminde hata oluştu.', 'danger')
    return redirect(url_for('club_games.index'))

@club_games_bp.route('/get/<int:game_id>')
@login_required
def get_match(game_id):
    match = ClubGameModel.get_match_details(game_id)
    return jsonify(match) if match else (jsonify({'error': 'Bulunamadı'}), 404)

@club_games_bp.route('/update/<int:game_id>', methods=['POST'])
@login_required
def update_match(game_id):
    if session.get('role') != 'admin':
        flash('Yetkiniz yok.', 'danger')
        return redirect(url_for('club_games.index'))
        
    try:
        ClubGameModel.update_match(
            game_id=game_id,
            date=request.form['date'],
            home_club_id=request.form['home_club_id'],
            away_club_id=request.form['away_club_id'],
            home_score=request.form['home_score'],
            away_score=request.form['away_score'],
            home_manager=request.form.get('home_manager'),
            away_manager=request.form.get('away_manager')
        )
        flash('Maç güncellendi.', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
    return redirect(url_for('club_games.index'))