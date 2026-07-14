import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'discord-bot-hosting-secret-key-change-in-production')
    
    # Use /tmp for Render (ephemeral filesystem)
    BASE_DIR = os.environ.get('RENDER', '') and '/tmp' or os.path.dirname(os.path.abspath(__file__))
    
    DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    BOTS_FOLDER = os.path.join(BASE_DIR, 'bots')
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    KEEP_ALIVE_INTERVAL = 30  # seconds
