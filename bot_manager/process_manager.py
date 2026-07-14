import os
import subprocess
import zipfile
import threading
import time
from config import Config

# Dictionary to store running processes
running_processes = {}

def extract_zip(zip_path, extract_path):
    """Extract zip file to specified path"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

def install_dependencies(bot_folder):
    """Install dependencies based on project files"""
    # Check for package.json (Node.js)
    if os.path.exists(os.path.join(bot_folder, 'package.json')):
        try:
            subprocess.run(
                ['npm', 'install'],
                cwd=bot_folder,
                capture_output=True,
                text=True,
                timeout=300
            )
            return True, 'Node.js dependencies installed'
        except Exception as e:
            return False, f'Failed to install Node.js dependencies: {str(e)}'
    
    # Check for requirements.txt (Python)
    if os.path.exists(os.path.join(bot_folder, 'requirements.txt')):
        try:
            subprocess.run(
                ['pip', 'install', '-r', 'requirements.txt'],
                cwd=bot_folder,
                capture_output=True,
                text=True,
                timeout=300
            )
            return True, 'Python dependencies installed'
        except Exception as e:
            return False, f'Failed to install Python dependencies: {str(e)}'
    
    return True, 'No dependencies to install'

def find_main_file(bot_folder):
    """Find the main file to run"""
    # Check for common main files
    common_files = ['index.js', 'main.js', 'bot.js', 'app.js', 'main.py', 'bot.py', 'app.py']
    
    for file in common_files:
        if os.path.exists(os.path.join(bot_folder, file)):
            return file
    
    # If no common file found, look for any .js or .py file
    for file in os.listdir(bot_folder):
        if file.endswith('.js') or file.endswith('.py'):
            return file
    
    return None

def start_bot(bot):
    """Start a bot"""
    from models import Bot
    
    bot_id = bot.id
    user_id = bot.user_id
    
    # Create bot folder
    bot_folder = os.path.join(Config.BOTS_FOLDER, str(bot_id))
    os.makedirs(bot_folder, exist_ok=True)
    
    # Extract zip file
    zip_path = os.path.join(Config.UPLOAD_FOLDER, str(user_id), bot.zip_filename)
    if not os.path.exists(zip_path):
        return False, 'ملف ZIP غير موجود'
    
    try:
        extract_zip(zip_path, bot_folder)
    except Exception as e:
        return False, f'فشل استخراج الملف: {str(e)}'
    
    # Install dependencies
    success, message = install_dependencies(bot_folder)
    if not success:
        return False, message
    
    # Find main file
    main_file = find_main_file(bot_folder)
    if not main_file:
        return False, 'لم يتم العثور على ملف رئيسي'
    
    # Determine command
    if main_file.endswith('.js'):
        command = ['node', main_file]
    elif main_file.endswith('.py'):
        command = ['python', main_file]
    else:
        return False, 'نوع الملف غير مدعوم'
    
    # Create log file
    log_file = os.path.join(Config.LOGS_FOLDER, f"{bot_id}.log")
    
    # Set environment variable for bot token
    env = os.environ.copy()
    env['DISCORD_TOKEN'] = bot.bot_token
    
    try:
        # Start process
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                command,
                cwd=bot_folder,
                stdout=f,
                stderr=subprocess.STDOUT,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
        
        # Store process
        running_processes[bot_id] = process
        
        # Update bot status
        bot.update_status('running', process.pid)
        
        return True, f'Bot started with PID {process.pid}'
    except Exception as e:
        return False, f'فشل تشغيل البوت: {str(e)}'

def stop_bot(bot):
    """Stop a bot"""
    from models import Bot
    
    bot_id = bot.id
    
    if bot_id in running_processes:
        process = running_processes[bot_id]
        try:
            process.terminate()
            process.wait(timeout=10)
        except:
            process.kill()
        
        del running_processes[bot_id]
    
    # Update bot status
    bot.update_status('stopped')
    
    return True, 'Bot stopped'

def get_bot_logs(bot_id, lines=100):
    """Get bot logs"""
    log_file = os.path.join(Config.LOGS_FOLDER, f"{bot_id}.log")
    
    if not os.path.exists(log_file):
        return []
    
    with open(log_file, 'r') as f:
        all_lines = f.readlines()
    
    return all_lines[-lines:]

def monitor_bots():
    """Monitor running bots and restart if needed"""
    while True:
        time.sleep(Config.KEEP_ALIVE_INTERVAL)
        
        from models import Bot
        
        # Get all running bots
        db = __import__('database').get_db()
        bots = db.execute('SELECT * FROM bots WHERE status = ?', ('running',)).fetchall()
        db.close()
        
        for bot_data in bots:
            bot_id = bot_data['id']
            
            # Check if process is still running
            if bot_id in running_processes:
                process = running_processes[bot_id]
                if process.poll() is not None:
                    # Process has stopped, restart it
                    bot = Bot.get_by_id(bot_id)
                    if bot:
                        print(f"Bot {bot_id} stopped, restarting...")
                        start_bot(bot)
            else:
                # Process not in dictionary, try to restart
                bot = Bot.get_by_id(bot_id)
                if bot:
                    print(f"Bot {bot_id} not in process list, restarting...")
                    start_bot(bot)

def start_monitor():
    """Start the bot monitor in a background thread"""
    monitor_thread = threading.Thread(target=monitor_bots, daemon=True)
    monitor_thread.start()
