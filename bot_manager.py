import os
import subprocess
import zipfile
import threading
import time
import shutil
import signal
from config import Config

running_processes = {}


def extract_zip(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_path)


def _which(cmd):
    try:
        subprocess.run(['which', cmd], capture_output=True, text=True, timeout=5, check=True)
        return True
    except Exception:
        return False

def install_dependencies(bot_folder):
    if os.path.exists(os.path.join(bot_folder, 'package.json')):
        if not _which('npm'):
            return False, 'Node.js غير مثبت في بيئة الاستضافة. لا يمكن تثبيت حزم npm.'
        try:
            r = subprocess.run(['npm', 'install'], cwd=bot_folder,
                              capture_output=True, text=True, timeout=300)
            if r.returncode != 0:
                return False, f'فشل تثبيت حزم npm: {r.stderr[:200]}'
            return True, 'Node.js dependencies installed'
        except Exception as e:
            return False, f'npm install failed: {str(e)}'
    if os.path.exists(os.path.join(bot_folder, 'requirements.txt')):
        try:
            r = subprocess.run(['pip', 'install', '-r', 'requirements.txt'],
                              cwd=bot_folder, capture_output=True, text=True, timeout=300)
            if r.returncode != 0:
                return False, f'فشل تثبيت حزم Python: {r.stderr[:200]}'
            return True, 'Python dependencies installed'
        except Exception as e:
            return False, f'pip install failed: {str(e)}'
    return True, 'No dependencies'


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
    from database import Bot as BotModel
    bot_id = bot.id
    user_id = bot.user_id
    bot_folder = os.path.join(Config.BOTS_FOLDER, str(bot_id))

    if os.path.exists(bot_folder):
        shutil.rmtree(bot_folder)
    os.makedirs(bot_folder, exist_ok=True)

    zip_path = os.path.join(Config.UPLOAD_FOLDER, str(user_id), bot.zip_filename)
    if not os.path.exists(zip_path):
        return False, 'ملف ZIP غير موجود'

    try:
        extract_zip(zip_path, bot_folder)
    except Exception as e:
        return False, f'فشل استخراج الملف: {str(e)}'

    success, msg = install_dependencies(bot_folder)
    if not success:
        return False, msg

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

    try:
        with open(log_file, 'w') as f:
            proc = subprocess.Popen(
                command, cwd=bot_folder, stdout=f, stderr=subprocess.STDOUT,
                env=env, preexec_fn=os.setsid if os.name == 'posix' else None
            )
        running_processes[bot_id] = proc
        bot.update_status('running', proc.pid)
        return True, f'تم التشغيل (PID: {proc.pid})'
    except Exception as e:
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
        time.sleep(Config.KEEP_ALIVE_INTERVAL)
        from database import get_db, Bot as BotModel
        with get_db() as db:
            bots = db.execute(
                'SELECT * FROM bots WHERE status = ?', ('running',)
            ).fetchall()
        for b in bots:
            bid = b['id']
            if bid in running_processes:
                proc = running_processes[bid]
                if proc.poll() is not None:
                    bot = BotModel.get_by_id(bid)
                    if bot:
                        start_bot(bot)
            else:
                bot = BotModel.get_by_id(bid)
                if bot:
                    start_bot(bot)


def start_monitor():
    t = threading.Thread(target=monitor_bots, daemon=True)
    t.start()
