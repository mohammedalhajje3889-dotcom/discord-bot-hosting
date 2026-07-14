import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-key-in-production')
    PORT = int(os.environ.get('PORT', 5000))
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    BOTS_FOLDER = os.path.join(BASE_DIR, 'bots')
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    KEEP_ALIVE_INTERVAL = 30
