from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import pymysql.cursors
from models.db import get_db_connection
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin yetkisi gerekiyor!', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Veri temizleme: 1452 hatasını önlemek için boş alanları NULL yapar
def clean_db_data(form_data):
    return {k: (v.strip() if v and v.strip() != "" else None) for k, v in form_data.items()}

@admin_bp.route('/table/<table_name>')
@admin_required
def view_table(table_name):
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # JOIN Tanımları: ID yerine isim göstermek için
            configs = {
                'players': {
                    'joins': "LEFT JOIN clubs c ON players.current_club_id = c.club_id",
                    'fields': "players.*, c.name as club_name",
                    'friendly': {'current_club_id': 'club_name'},
                    'filters': ['name', 'position', 'country_of_citizenship']
                },
                'clubs': {
                    'joins': "LEFT JOIN competitions comp ON clubs.domestic_competition_id = comp.competition_id",
                    'fields': "clubs.*, comp.name as comp_name",
                    'friendly': {'domestic_competition_id': 'comp_name'},
                    'filters': ['name', 'stadium_name']
                },
                'player_valuations': {
                    'joins': "LEFT JOIN players p ON player_valuations.player_id = p.player_id",
                    'fields': "player_valuations.*, p.name as p_name",
                    'friendly': {'player_id': 'p_name'},
                    'filters': ['player_id', 'date']
                }
            }

            cfg = configs.get(table_name, {'joins': "", 'fields': f"`{table_name}`.*", 'friendly': {}, 'filters': []})
            
            # Filtreleme Mantığı
            where_clauses = []
            params = []
            for f_col in cfg.get('filters', []):
                val = request.args.get(f_col)
                if val:
                    where_clauses.append(f"`{table_name}`.`{f_col}` LIKE %s")
                    params.append(f"%{val}%")
            
            where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            # Veri Çekme
            query = f"SELECT {cfg['fields']} FROM `{table_name}` {cfg['joins']} {where_str} LIMIT %s OFFSET %s"
            cursor.execute(query, params + [per_page, offset])
            rows = cursor.fetchall()

            # Toplam Sayfa Sayısı
            cursor.execute(f"SELECT COUNT(*) as total FROM `{table_name}` {where_str}", params)
            total_pages = (cursor.fetchone()['total'] + per_page - 1) // per_page

            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            pk = next((c['Field'] for c in columns if c['Key'] == 'PRI'), columns[0]['Field'])

        return render_template('admin/view_table.html', table_name=table_name, rows=rows, columns=columns, pk=pk, 
                               page=page, total_pages=total_pages, friendly_map=cfg['friendly'], 
                               active_filters=cfg['filters'], filters=request.args)
    finally:
        conn.close()

@admin_bp.route('/delete/<table_name>/<pk_col>/<pk_val>')
@admin_required
def delete_record(table_name, pk_col, pk_val):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = %s", (pk_val,))
            conn.commit()
            flash('Kayıt başarıyla silindi.', 'success')
    except Exception as e:
        flash(f'Silme hatası: {str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin.view_table', table_name=table_name))

# --- Ekleme, Düzenleme ve Index rotaları önceki sürümlerdeki gibi kalacak ---
@admin_bp.route('/')
@admin_required
def index():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Gerçek Sayıları Çekiyoruz
            cursor.execute("SELECT COUNT(*) as total FROM players")
            player_count = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM clubs")
            club_count = cursor.fetchone()['total']
            
            # Navbardaki 'Games' ismine istinaden tablonun 'games' olduğunu varsayıyorum
            cursor.execute("SELECT COUNT(*) as total FROM games")
            game_count = cursor.fetchone()['total']
            
            # 2. Mevcut tablo listesini çekiyoruz (Sayfanın altındaki liste için)
            cursor.execute("SHOW TABLES")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
            
        return render_template('admin/index.html', 
                               tables=tables, 
                               player_count=player_count, 
                               club_count=club_count, 
                               game_count=game_count)
    finally:
        conn.close()
        
@admin_bp.route('/add/<table_name>', methods=['GET', 'POST'])
@admin_required
def add_record(table_name):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"DESCRIBE `{table_name}`")
        cols_info = cursor.fetchall()
        if request.method == 'POST':
            data = clean_db_data({c['Field']: request.form.get(c['Field']) for c in cols_info if 'auto_increment' not in c['Extra']})
            if table_name == 'players':
                data['name'] = f"{data.get('first_name') or ''} {data.get('last_name') or ''}".strip() or None
            keys = ", ".join([f"`{k}`" for k in data.keys()]); vals = ", ".join(["%s"] * len(data))
            cursor.execute(f"INSERT INTO `{table_name}` ({keys}) VALUES ({vals})", list(data.values()))
            conn.commit()
            flash('Başarıyla eklendi.', 'success')
            return redirect(url_for('admin.view_table', table_name=table_name))
        display_cols = [c for c in cols_info if 'auto_increment' not in c['Extra']]
        return render_template('admin/edit_record.html', table_name=table_name, columns=display_cols, record=None)
    finally:
        conn.close()

@admin_bp.route('/edit/<table_name>/<pk_col>/<pk_val>', methods=['GET', 'POST'])
@admin_required
def edit_record(table_name, pk_col, pk_val):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            cursor.execute(f"DESCRIBE `{table_name}`")
            cols_info = cursor.fetchall()
            update_data = clean_db_data({c['Field']: request.form.get(c['Field']) for c in cols_info if c['Field'] != pk_col})
            if table_name == 'players':
                update_data['name'] = f"{update_data.get('first_name') or ''} {update_data.get('last_name') or ''}".strip() or None
            set_clause = ", ".join([f"`{k}` = %s" for k in update_data.keys()])
            cursor.execute(f"UPDATE `{table_name}` SET {set_clause} WHERE `{pk_col}` = %s", list(update_data.values()) + [pk_val])
            conn.commit()
            flash('Güncellendi.', 'success')
            return redirect(url_for('admin.view_table', table_name=table_name))
        cursor.execute(f"SELECT * FROM `{table_name}` WHERE `{pk_col}` = %s", (pk_val,))
        record = cursor.fetchone()
        cursor.execute(f"DESCRIBE `{table_name}`")
        return render_template('admin/edit_record.html', table_name=table_name, columns=cursor.fetchall(), record=record, pk_col=pk_col)
    finally:
        conn.close()