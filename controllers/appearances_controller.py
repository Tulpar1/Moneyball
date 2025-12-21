from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from models.appearances_model import AppearanceModel
from functools import wraps

appearances_bp = Blueprint('appearances', __name__, url_prefix='/appearances')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@appearances_bp.route('/')
@login_required
def index():
    try:
        search = request.args.get('q')
        min_min = request.args.get('min_minutes')
        page = request.args.get('page', 1, type=int)
        per_page = 20

        appearances_data, total_count = AppearanceModel.get_all_appearances(search, min_min, page, per_page)
        total_pages = (total_count + per_page - 1) // per_page

        return render_template('appearances/index.html', 
                               appearances=appearances_data, 
                               page=page, 
                               total_pages=total_pages,
                               current_search=search,
                               current_min=min_min)
    except Exception as e:
        flash(f"Performans verileri yüklenirken hata: {str(e)}", 'danger')
        return redirect(url_for('main.index'))