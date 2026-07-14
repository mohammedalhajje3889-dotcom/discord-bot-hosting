from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Bot
from bot_manager.process_manager import start_bot, stop_bot, get_bot_logs

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    bots = Bot.get_by_user_id(current_user.id)
    return render_template('dashboard/index.html', bots=bots)

@dashboard_bp.route('/bot/new', methods=['GET', 'POST'])
@login_required
def new_bot():
    if request.method == 'POST':
        name = request.form.get('name')
        bot_token = request.form.get('bot_token')
        
        if not name or not bot_token:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('dashboard/bot_form.html')
        
        # Handle zip file upload
        if 'zip_file' not in request.files:
            flash('يرجى رفع ملف ZIP', 'error')
            return render_template('dashboard/bot_form.html')
        
        zip_file = request.files['zip_file']
        if zip_file.filename == '':
            flash('لم يتم اختيار ملف', 'error')
            return render_template('dashboard/bot_form.html')
        
        if not zip_file.filename.endswith('.zip'):
            flash('يجب أن يكون الملف بصيغة ZIP', 'error')
            return render_template('dashboard/bot_form.html')
        
        try:
            # Save zip file
            import os
            from config import Config
            
            # Create user folder
            user_folder = os.path.join(Config.UPLOAD_FOLDER, str(current_user.id))
            os.makedirs(user_folder, exist_ok=True)
            
            zip_filename = f"{name}_{current_user.id}.zip"
            zip_path = os.path.join(user_folder, zip_filename)
            zip_file.save(zip_path)
            
            # Create bot in database
            bot = Bot.create(current_user.id, name, bot_token, zip_filename)
            
            flash('تم إنشاء البوت بنجاح', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash(f'حدث خطأ: {str(e)}', 'error')
            return render_template('dashboard/bot_form.html')
    
    return render_template('dashboard/bot_form.html')

@dashboard_bp.route('/bot/<int:bot_id>/update', methods=['GET', 'POST'])
@login_required
def update_bot(bot_id):
    bot = Bot.get_by_id(bot_id)
    if not bot or bot.user_id != current_user.id:
        flash('البوت غير موجود', 'error')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        bot_token = request.form.get('bot_token')
        
        if not name or not bot_token:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('dashboard/bot_form.html', bot=bot, update=True)
        
        import os
        from config import Config
        import shutil
        
        if 'zip_file' in request.files and request.files['zip_file'].filename:
            zip_file = request.files['zip_file']
            if not zip_file.filename.endswith('.zip'):
                flash('يجب أن يكون الملف بصيغة ZIP', 'error')
                return render_template('dashboard/bot_form.html', bot=bot, update=True)
            
            # Delete old zip
            old_zip = os.path.join(Config.UPLOAD_FOLDER, str(current_user.id), bot.zip_filename)
            if os.path.exists(old_zip):
                os.remove(old_zip)
            
            # Save new zip
            user_folder = os.path.join(Config.UPLOAD_FOLDER, str(current_user.id))
            os.makedirs(user_folder, exist_ok=True)
            zip_filename = f"{name}_{current_user.id}.zip"
            zip_path = os.path.join(user_folder, zip_filename)
            zip_file.save(zip_path)
            bot.zip_filename = zip_filename
            
            # Delete extracted bot folder so it gets re-extracted on next start
            bot_folder = os.path.join(Config.BOTS_FOLDER, str(bot_id))
            if os.path.exists(bot_folder):
                shutil.rmtree(bot_folder)
            
            # Stop bot if running
            if bot.status == 'running':
                from bot_manager.process_manager import stop_bot
                stop_bot(bot)
        
        # Update database
        bot.update(name=name, bot_token=bot_token)
        bot.status = 'stopped'
        bot.update_status('stopped')
        
        flash('تم تحديث البوت بنجاح', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('dashboard/bot_form.html', bot=bot, update=True)

@dashboard_bp.route('/bot/<int:bot_id>/start', methods=['POST'])
@login_required
def start_bot_route(bot_id):
    bot = Bot.get_by_id(bot_id)
    if not bot or bot.user_id != current_user.id:
        flash('البوت غير موجود', 'error')
        return redirect(url_for('dashboard.index'))
    
    if bot.status == 'running':
        flash('البوت يعمل بالفعل', 'warning')
        return redirect(url_for('dashboard.index'))
    
    success, message = start_bot(bot)
    if success:
        flash(f'تم تشغيل البوت: {message}', 'success')
    else:
        flash(f'فشل تشغيل البوت: {message}', 'error')
    
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/bot/<int:bot_id>/stop', methods=['POST'])
@login_required
def stop_bot_route(bot_id):
    bot = Bot.get_by_id(bot_id)
    if not bot or bot.user_id != current_user.id:
        flash('البوت غير موجود', 'error')
        return redirect(url_for('dashboard.index'))
    
    if bot.status != 'running':
        flash('البوت غير يعمل', 'warning')
        return redirect(url_for('dashboard.index'))
    
    success, message = stop_bot(bot)
    if success:
        flash(f'تم إيقاف البوت: {message}', 'success')
    else:
        flash(f'فشل إيقاف البوت: {message}', 'error')
    
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/bot/<int:bot_id>/delete', methods=['POST'])
@login_required
def delete_bot(bot_id):
    bot = Bot.get_by_id(bot_id)
    if not bot or bot.user_id != current_user.id:
        flash('البوت غير موجود', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Stop bot if running
    if bot.status == 'running':
        stop_bot(bot)
    
    # Delete files
    import os
    from config import Config
    
    # Delete zip file
    zip_path = os.path.join(Config.UPLOAD_FOLDER, str(current_user.id), bot.zip_filename)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    # Delete bot folder
    bot_folder = os.path.join(Config.BOTS_FOLDER, str(bot_id))
    if os.path.exists(bot_folder):
        import shutil
        shutil.rmtree(bot_folder)
    
    # Delete log file
    log_file = os.path.join(Config.LOGS_FOLDER, f"{bot_id}.log")
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Delete from database
    bot.delete()
    
    flash('تم حذف البوت بنجاح', 'success')
    return redirect(url_for('dashboard.index'))
