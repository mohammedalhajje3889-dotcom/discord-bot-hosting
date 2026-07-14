import sqlite3
from contextlib import contextmanager
from flask_login import UserMixin
from config import Config


@contextmanager
def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                bot_token TEXT NOT NULL,
                zip_filename TEXT,
                status TEXT DEFAULT 'stopped',
                process_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')


class User(UserMixin):
    def __init__(self, id, username, email, password_hash, created_at):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def get_by_id(user_id):
        with get_db() as db:
            user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return None
        return User(**user)

    @staticmethod
    def get_by_username(username):
        with get_db() as db:
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if not user:
            return None
        return User(**user)

    @staticmethod
    def get_by_email(email):
        with get_db() as db:
            user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if not user:
            return None
        return User(**user)

    @staticmethod
    def create(username, email, password_hash):
        with get_db() as db:
            db.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            user_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        return User.get_by_id(user_id)


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
        with get_db() as db:
            bot = db.execute('SELECT * FROM bots WHERE id = ?', (bot_id,)).fetchone()
        if not bot:
            return None
        return Bot(**bot)

    @staticmethod
    def get_by_user_id(user_id):
        with get_db() as db:
            bots = db.execute(
                'SELECT * FROM bots WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            ).fetchall()
        return [Bot(**bot) for bot in bots]

    @staticmethod
    def create(user_id, name, bot_token, zip_filename):
        with get_db() as db:
            db.execute(
                'INSERT INTO bots (user_id, name, bot_token, zip_filename) VALUES (?, ?, ?, ?)',
                (user_id, name, bot_token, zip_filename)
            )
            bot_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        return Bot.get_by_id(bot_id)

    def update(self, name=None, bot_token=None, zip_filename=None):
        with get_db() as db:
            if name:
                db.execute('UPDATE bots SET name = ? WHERE id = ?', (name, self.id))
                self.name = name
            if bot_token:
                db.execute('UPDATE bots SET bot_token = ? WHERE id = ?', (bot_token, self.id))
                self.bot_token = bot_token
            if zip_filename:
                db.execute('UPDATE bots SET zip_filename = ? WHERE id = ?', (zip_filename, self.id))
                self.zip_filename = zip_filename

    def update_status(self, status, process_id=None):
        with get_db() as db:
            if process_id is not None:
                db.execute('UPDATE bots SET status = ?, process_id = ? WHERE id = ?',
                          (status, process_id, self.id))
            else:
                db.execute('UPDATE bots SET status = ? WHERE id = ?', (status, self.id))
        self.status = status
        if process_id is not None:
            self.process_id = process_id

    def delete(self):
        with get_db() as db:
            db.execute('DELETE FROM bots WHERE id = ?', (self.id,))
