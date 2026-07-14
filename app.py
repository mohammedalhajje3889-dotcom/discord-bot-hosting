import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database import init_db, User, Bot
from bot_manager import start_bot, stop_bot, get_bot_logs, start_prepare_async, start_monitor

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = Config.SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول لهذه الصفحة'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='الصفحة غير موجودة'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='حدث خطأ داخلي في الخادم'), 500


os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.BOTS_FOLDER, exist_ok=True)
os.makedirs(Config.LOGS_FOLDER, exist_ok=True)
init_db()
start_monitor()


# ── Auth Routes ──

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=bool(request.form.get('remember')))
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if not username or not email or not password:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('كلمتا المرور غير متطابقتين', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
            return render_template('register.html')
        if User.get_by_username(username):
            flash('اسم المستخدم موجود بالفعل', 'error')
            return render_template('register.html')
        if User.get_by_email(email):
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('register.html')
        try:
            user = User.create(username, email, generate_password_hash(password))
            login_user(user)
            flash('تم إنشاء الحساب بنجاح', 'success')
            return redirect(url_for('dashboard'))
        except Exception:
            flash('حدث خطأ أثناء إنشاء الحساب', 'error')
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))


# ── Dashboard Routes ──

@app.route('/')
@login_required
def dashboard():
    bots = Bot.get_by_user_id(current_user.id)
    return render_template('dashboard.html', bots=bots)


@app.route('/bot/new', methods=['GET', 'POST'])
@login_required
def new_bot():
    if request.method == 'POST':
        name = request.form.get('name')
        bot_token = request.form.get('bot_token')
        if not name or not bot_token:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('bot_form.html')
        if 'zip_file' not in request.files:
            flash('يرجى رفع ملف ZIP', 'error')
            return render_template('bot_form.html')
        zip_file = request.files['zip_file']
        if not zip_file.filename or not zip_file.filename.endswith('.zip'):
            flash('يجب رفع ملف بصيغة ZIP', 'error')
            return render_template('bot_form.html')
        try:
            user_folder = os.path.join(Config.UPLOAD_FOLDER, str(current_user.id))
            os.makedirs(user_folder, exist_ok=True)
            zip_filename = f'{name}_{current_user.id}.zip'
            zip_file.save(os.path.join(user_folder, zip_filename))
            bot = Bot.create(current_user.id, name, bot_token, zip_filename)

            # Prepare bot folder in background (extract + install deps)
            start_prepare_async(bot)

            flash('تم إنشاء البوت بنجاح. جاري تجهيز الملفات...', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'حدث خطأ: {str(e)}', 'error')
    return render_template('bot_form.html')


@app.route('/bot/<int:bot_id>')
@login_required
def view_bot(bot_id):
    bot = Bot.get_by_id(bot_id)
    if not bot or bot.user_id != current_user.id:
        flash('البوت غير موجود', 'error')
        return redirect(url_for('dashboard'))
    logs = get_bot_logs(bot_id)
    return render_template('bot_logs.html', bot=bot, logs=logs)


@app.route('/bot/<int:bot_id>/update', methods=['GET', 'POST'])
@login_required
def update_bot(bot_id):
    bot = Bot.get_by_id(bot_id)
    if not bot or bot.user_id != current_user.id:
        flash('البوت غير موجود', 'error')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name')
        bot_token = request.form.get('bot_token')
        if not name or not bot_token:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('bot_form.html', bot=bot, update=True)
        if 'zip_file' in request.files and request.files['zip_file'].filename:
            zip_file = request.files['zip_file']
            if not zip_file.filename.endswith('.zip'):
                flash('يجب أن يكون الملف بصيغة ZIP', 'error')
                return render_template('bot_form.html', bot=bot, update=True)
            user_folder = os.path.join(Config.UPLOAD_FOLDER, str(current_user.id))
            zf = os.path.join(user_folder, bot.zip_filename)
            if os.path.exists(zf):
                os.remove(zf)
            zip_filename = f'{name}_{current_user.id}.zip'
            zip_file.save(os.path.join(user_folder, zip_filename))
            bot.zip_filename = zip_filename
            if bot.status == 'running':
                stop_bot(bot)
            start_prepare_async(bot)
            flash('جاري تجهيز الملفات...', 'success')
            return redirect(url_for('dashboard'))
        bot.update(name=name, bot_token=bot_token)
        bot.update_status('stopped')
        flash('تم تحديث البوت بنجاح', 'success')
        return redirect(url_for('dashboard'))
    return render_template('bot_form.html', bot=bot, update=True)


@app.route('/bot/<int:bot_id>/start', methods=['POST'])
@login_required
def start_bot_route(bot_id):
    bot = Bot.get_by_id(bot_id)
    if not bot or bot.user_id != current_user.id:
        flash('البوت غير موجود', 'error')
        return redirect(url_for('dashboard'))
    if bot.status == 'running':
        flash('البوت يعمل بالفعل', 'warning')
        return redirect(url_for('dashboard'))
    if bot.status == 'preparing':
        flash('البوت قيد التجهيز، الرجاء الانتظار', 'warning')
        return redirect(url_for('dashboard'))
    ok, msg = start_bot(bot)
    if not ok:
        # Ensure status is marked stopped on failure
        bot.update_status('stopped')
    flash(msg, 'success' if ok else 'error')
    return redirect(url_for('dashboard'))


@app.route('/bot/<int:bot_id>/stop', methods=['POST'])
@login_required
def stop_bot_route(bot_id):
    bot = Bot.get_by_id(bot_id)
    if not bot or bot.user_id != current_user.id:
        flash('البوت غير موجود', 'error')
        return redirect(url_for('dashboard'))
    if bot.status not in ('running', 'error'):
        flash('البوت غير يعمل', 'warning')
        return redirect(url_for('dashboard'))
    ok, msg = stop_bot(bot)
    if bot.status == 'error':
        bot.update_status('stopped')
    flash(msg, 'success' if ok else 'error')
    return redirect(url_for('dashboard'))


@app.route('/bot/<int:bot_id>/delete', methods=['POST'])
@login_required
def delete_bot(bot_id):
    bot = Bot.get_by_id(bot_id)
    if not bot or bot.user_id != current_user.id:
        flash('البوت غير موجود', 'error')
        return redirect(url_for('dashboard'))
    if bot.status == 'running':
        stop_bot(bot)
    for p in [
        os.path.join(Config.UPLOAD_FOLDER, str(current_user.id), bot.zip_filename),
        os.path.join(Config.BOTS_FOLDER, str(bot_id)),
        os.path.join(Config.LOGS_FOLDER, f'{bot_id}.log'),
    ]:
        if os.path.isdir(p):
            import shutil
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    bot.delete()
    flash('تم حذف البوت بنجاح', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=False)
