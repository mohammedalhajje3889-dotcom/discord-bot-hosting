from flask_login import UserMixin
from database import get_db

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, created_at):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
    
    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        db.close()
        if user:
            return User(
                id=user['id'],
                username=user['username'],
                email=user['email'],
                password_hash=user['password_hash'],
                created_at=user['created_at']
            )
        return None
    
    @staticmethod
    def get_by_username(username):
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()
        if user:
            return User(
                id=user['id'],
                username=user['username'],
                email=user['email'],
                password_hash=user['password_hash'],
                created_at=user['created_at']
            )
        return None
    
    @staticmethod
    def get_by_email(email):
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        db.close()
        if user:
            return User(
                id=user['id'],
                username=user['username'],
                email=user['email'],
                password_hash=user['password_hash'],
                created_at=user['created_at']
            )
        return None
    
    @staticmethod
    def create(username, email, password_hash):
        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            db.commit()
            user_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            db.close()
            return User.get_by_id(user_id)
        except Exception as e:
            db.close()
            raise e

class Bot:
    def __init__(self, id, user_id, name, bot_token, zip_filename, status, process_id, created_at):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.bot_token = bot_token
        self.zip_filename = zip_filename
        self.status = status
        self.process_id = process_id
        self.created_at = created_at
    
    @staticmethod
    def get_by_id(bot_id):
        db = get_db()
        bot = db.execute('SELECT * FROM bots WHERE id = ?', (bot_id,)).fetchone()
        db.close()
        if bot:
            return Bot(
                id=bot['id'],
                user_id=bot['user_id'],
                name=bot['name'],
                bot_token=bot['bot_token'],
                zip_filename=bot['zip_filename'],
                status=bot['status'],
                process_id=bot['process_id'],
                created_at=bot['created_at']
            )
        return None
    
    @staticmethod
    def get_by_user_id(user_id):
        db = get_db()
        bots = db.execute('SELECT * FROM bots WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
        db.close()
        return [
            Bot(
                id=bot['id'],
                user_id=bot['user_id'],
                name=bot['name'],
                bot_token=bot['bot_token'],
                zip_filename=bot['zip_filename'],
                status=bot['status'],
                process_id=bot['process_id'],
                created_at=bot['created_at']
            )
            for bot in bots
        ]
    
    @staticmethod
    def create(user_id, name, bot_token, zip_filename):
        db = get_db()
        try:
            db.execute(
                'INSERT INTO bots (user_id, name, bot_token, zip_filename) VALUES (?, ?, ?, ?)',
                (user_id, name, bot_token, zip_filename)
            )
            db.commit()
            bot_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            db.close()
            return Bot.get_by_id(bot_id)
        except Exception as e:
            db.close()
            raise e
    
    def update_status(self, status, process_id=None):
        db = get_db()
        if process_id is not None:
            db.execute('UPDATE bots SET status = ?, process_id = ? WHERE id = ?', (status, process_id, self.id))
        else:
            db.execute('UPDATE bots SET status = ? WHERE id = ?', (status, self.id))
        db.commit()
        db.close()
        self.status = status
        if process_id is not None:
            self.process_id = process_id
    
    def update(self, name=None, bot_token=None, zip_filename=None):
        db = get_db()
        if name:
            db.execute('UPDATE bots SET name = ? WHERE id = ?', (name, self.id))
            self.name = name
        if bot_token:
            db.execute('UPDATE bots SET bot_token = ? WHERE id = ?', (bot_token, self.id))
            self.bot_token = bot_token
        if zip_filename:
            db.execute('UPDATE bots SET zip_filename = ? WHERE id = ?', (zip_filename, self.id))
            self.zip_filename = zip_filename
        db.commit()
        db.close()

    def delete(self):
        db = get_db()
        db.execute('DELETE FROM bots WHERE id = ?', (self.id,))
        db.commit()
        db.close()
