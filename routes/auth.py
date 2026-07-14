from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.get_by_username(username)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('كلمتا المرور غير متطابقتين', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
            return render_template('auth/register.html')
        
        # Check if username or email exists
        if User.get_by_username(username):
            flash('اسم المستخدم موجود بالفعل', 'error')
            return render_template('auth/register.html')
        
        if User.get_by_email(email):
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('auth/register.html')
        
        # Create user
        try:
            password_hash = generate_password_hash(password)
            user = User.create(username, email, password_hash)
            login_user(user)
            flash('تم إنشاء الحساب بنجاح', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash('حدث خطأ أثناء إنشاء الحساب', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('auth.login'))
