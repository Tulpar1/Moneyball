from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import hashlib
import re
import pymysql.cursors
from datetime import datetime
from models.db import get_db_connection 

auth_bp = Blueprint('auth', __name__)

def md5_hash(password):
    return hashlib.md5(password.encode()).hexdigest()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'user')
        
        if password != confirm_password:
            flash('Parolalar eşleşmiyor!', 'danger')
            return render_template('auth/register.html')
        
        try:
            connection = get_db_connection()
            # PyMySQL için DictCursor kullanımı
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                if cursor.fetchone():
                    flash('Bu email adresi zaten kayıtlı!', 'danger')
                else:
                    hashed_password = md5_hash(password)
                    cursor.execute(
                        'INSERT INTO users (full_name, email, password, role, created_at) VALUES (%s, %s, %s, %s, %s)', 
                        (full_name, email, hashed_password, role, datetime.now())
                    )
                    connection.commit()
                    flash('Kayıt başarılı!', 'success')
                    return redirect(url_for('auth.login'))
        finally:
            if 'connection' in locals(): connection.close()
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = md5_hash(password)
        
        try:
            connection = get_db_connection()
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, hashed_password))
                account = cursor.fetchone()
            
            if account:
                session['user_id'] = account['user_id']
                session['full_name'] = account['full_name']
                session['role'] = account['role'] # Admin yetkisi için kritik
                return redirect(url_for('main.dashboard'))
            else:
                flash('Geçersiz bilgiler!', 'danger')
        finally:
            if 'connection' in locals(): connection.close()
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('main.index'))