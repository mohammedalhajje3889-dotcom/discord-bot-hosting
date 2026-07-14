import os
import subprocess
import zipfile
import threading
import time
import shutil
import signal
from config import Config

running_processes = {}
restart_counts = {}


def extract_zip(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_path)


def _which(cmd):
    try:
        subprocess.run(['which', cmd], capture_output=True, text=True, timeout=5, check=True)
        return True
    except Exception:
        return False


def find_package_root(bot_folder, filename):
    for root, dirs, files in os.walk(bot_folder):
        if filename in files:
            return root
    return None


def install_dependencies(bot_folder):
    pjson_dir = find_package_root(bot_folder, 'package.json')
    if pjson_dir:
        if not _which('npm'):
            return False, 'Node.js غير مثبت في بيئة الاستضافة.'
        try:
            r = subprocess.run(['npm', 'install'], cwd=pjson_dir,
                              capture_output=True, text=True, timeout=300)
            if r.returncode != 0:
                return False, f'فشل npm install: {r.stderr[:200]}'
            return True, 'Node.js dependencies installed'
        except Exception as e:
            return False, f'npm install failed: {str(e)}'

    req_dir = find_package_root(bot_folder, 'requirements.txt')
    if req_dir:
        try:
            r = subprocess.run(
                ['pip', 'install', '-r', os.path.join(req_dir, 'requirements.txt')],
                capture_output=True, text=True, timeout=300)
            if r.returncode != 0:
                return False, f'فشل pip install: {r.stderr[:200]}'
            return True, 'Python dependencies installed'
        except Exception as e:
            return False, f'pip install failed: {str(e)}'

    return True, 'No dependencies'


def prepare_bot_folder(bot):
    """Extract ZIP and install dependencies. Runs synchronously or in thread."""
    bot_folder = os.path.join(Config.BOTS_FOLDER, str(bot.id))
    if os.path.exists(bot_folder):
        shutil.rmtree(bot_folder)
    os.makedirs(bot_folder, exist_ok=True)

    zip_path = os.path.join(Config.UPLOAD_FOLDER, str(bot.user_id), bot.zip_filename)
    if not os.path.exists(zip_path):
        return False, 'ملف ZIP غير موجود'

    try:
        extract_zip(zip_path, bot_folder)
    except Exception as e:
        return False, f'فشل استخراج الملف: {str(e)}'

    ok, msg = install_dependencies(bot_folder)
    if not ok:
        shutil.rmtree(bot_folder)
        return False, msg
    return True, 'تم تجهيز البوت'


def _prepare_async(bot):
    """Prepare bot folder asynchronously and update status."""
    ok, msg = prepare_bot_folder(bot)
    if ok:
        bot.update_status('stopped')
    else:
        bot.update_status('error')


def start_prepare_async(bot):
    """Start preparing bot in background thread, returns immediately."""
    from database import Bot as BotModel
    b = BotModel.get_by_id(bot.id)
    if b:
        b.update_status('preparing')
    t = threading.Thread(target=_prepare_async, args=(bot,), daemon=True)
    t.start()


def find_main_file(bot_folder):
    common = ['index.js', 'main.js', 'bot.js', 'app.js',
              'main.py', 'bot.py', 'app.py', 'run.py', 'server.py']
    for root, dirs, files in os.walk(bot_folder):
        for f in files:
            if f in common:
                return os.path.relpath(os.path.join(root, f), bot_folder)
    for root, dirs, files in os.walk(bot_folder):
        for f in files:
            if f.endswith(('.js', '.py')):
                return os.path.relpath(os.path.join(root, f), bot_folder)
    return None


def list_extracted_files(bot_folder):
    files = []
    for root, dirs, fnames in os.walk(bot_folder):
        for f in fnames:
            files.append(os.path.relpath(os.path.join(root, f), bot_folder))
    return files


def start_bot(bot):
    bot_id = bot.id
    bot_folder = os.path.join(Config.BOTS_FOLDER, str(bot_id))

    if not os.path.exists(bot_folder):
        return False, 'البوت غير جاهز. الرجاء إعادة رفع الملف.'

    main_file = find_main_file(bot_folder)
    if not main_file:
        flist = list_extracted_files(bot_folder)
        return False, f'لم يتم العثور على ملف رئيسي. الملفات: {flist[:15]}'

    if main_file.endswith('.py'):
        command = ['python3' if os.name == 'posix' else 'python', main_file]
    elif main_file.endswith('.js'):
        if not _which('node'):
            return False, 'Node.js غير مثبت في بيئة الاستضافة. لا يمكن تشغيل بوتات JavaScript.'
        command = ['node', main_file]
    else:
        return False, 'نوع الملف غير مدعوم'

    log_file = os.path.join(Config.LOGS_FOLDER, f'{bot_id}.log')
    env = os.environ.copy()
    env['DISCORD_TOKEN'] = bot.bot_token
    env['BOT_TOKEN'] = bot.bot_token

    # Kill old process if hanging
    if bot_id in running_processes:
        try:
            running_processes[bot_id].kill()
        except Exception:
            pass
        del running_processes[bot_id]

    try:
        with open(log_file, 'w') as f:
            proc = subprocess.Popen(
                command, cwd=bot_folder, stdout=f, stderr=subprocess.STDOUT,
                env=env, preexec_fn=os.setsid if os.name == 'posix' else None
            )

        # Verify it stays alive (1s, 3s, 5s)
        checks = [1, 3, 5]
        total = 0
        for s in checks:
            time.sleep(s)
            total += s
            if proc.poll() is not None:
                err_lines = get_bot_logs(bot_id, lines=8)
                err_msg = err_lines[-1].strip() if err_lines else 'خطأ غير معروف'
                bot.update_status('stopped')
                return False, f'توقف البوت بعد {total}ث: {err_msg}'

        running_processes[bot_id] = proc
        bot.update_status('running', proc.pid)
        return True, f'تم التشغيل بنجاح (PID: {proc.pid})'
    except Exception as e:
        bot.update_status('stopped')
        return False, f'فشل التشغيل: {str(e)}'


def stop_bot(bot):
    bot_id = bot.id
    if bot_id in running_processes:
        proc = running_processes[bot_id]
        try:
            if os.name == 'posix':
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            else:
                proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        del running_processes[bot_id]
    bot.update_status('stopped')
    restart_counts.pop(bot_id, None)
    return True, 'تم الإيقاف'


def get_bot_logs(bot_id, lines=100):
    log_file = os.path.join(Config.LOGS_FOLDER, f'{bot_id}.log')
    if not os.path.exists(log_file):
        return []
    with open(log_file, 'r') as f:
        all_lines = f.readlines()
    return all_lines[-lines:]


def monitor_bots():
    while True:
        time.sleep(Config.KEEP_ALIVE_INTERVAL / 2)
        from database import get_db, Bot as BotModel
        now = time.time()
        with get_db() as db:
            bots = db.execute(
                'SELECT * FROM bots WHERE status = ?', ('running',)
            ).fetchall()
        for b in bots:
            bid = b['id']
            for rid in list(restart_counts.keys()):
                if now - restart_counts[rid]['time'] > 300:
                    del restart_counts[rid]

            proc = running_processes.get(bid)
            if proc and proc.poll() is not None:
                rc = restart_counts.get(bid, {'count': 0, 'time': now})
                rc['count'] += 1
                rc['time'] = now
                restart_counts[bid] = rc
                if rc['count'] > 3:
                    bot = BotModel.get_by_id(bid)
                    if bot:
                        bot.update_status('error')
                        del running_processes[bid]
                        restart_counts.pop(bid, None)
                    continue
                bot = BotModel.get_by_id(bid)
                if bot:
                    start_bot(bot)
            elif bid not in running_processes:
                bot = BotModel.get_by_id(bid)
                if bot:
                    start_bot(bot)


def start_monitor():
    t = threading.Thread(target=monitor_bots, daemon=True)
    t.start()
