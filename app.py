import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from database import init_db
from models import User
from bot_manager.process_manager import start_monitor

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول لهذه الصفحة'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

# Register blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

# Create necessary directories
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.BOTS_FOLDER, exist_ok=True)
os.makedirs(Config.LOGS_FOLDER, exist_ok=True)

# Initialize database
init_db()

# Start bot monitor
start_monitor()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
