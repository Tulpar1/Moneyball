from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from models.competitions_model import CompetitionModel
from functools import wraps

competitions_bp = Blueprint('competitions', __name__, url_prefix='/competitions')

def format_text(text):
    if not text: return ""
    return text.replace('-', ' ').replace('_', ' ').title()

# Yetki kontrolü (Daha önce Clubs'a eklediysen oradan da import edebilirsin)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@competitions_bp.route('/')
@login_required
def index():
    try:
        search = request.args.get('q')
        type_f = request.args.get('type')
        page = request.args.get('page', 1, type=int)
        per_page = 15

        comps, total_count = CompetitionModel.get_all_competitions(search, type_f, page=page, per_page=per_page)
        total_pages = (total_count + per_page - 1) // per_page

        return render_template('competitions/index.html', 
                               competitions=comps, 
                               page=page, 
                               total_pages=total_pages,
                               current_search=search,
                               current_type=type_f)
    except Exception as e:
        flash(f"Hata: {str(e)}", 'danger')
        return redirect(url_for('main.index'))

@competitions_bp.route('/get/<competition_id>')
@login_required
def get_competition(competition_id):
    comp = CompetitionModel.get_competition_by_id(competition_id)
    return jsonify(comp) if comp else (jsonify({'error': 'Not found'}), 404)
