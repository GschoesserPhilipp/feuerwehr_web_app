from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class ErrorList(db.Model):
    __tablename__ = 'error_texts'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.Integer, primary_key=True)
    error_text = db.Column(db.String, nullable=False)
    time = db.Column(db.Integer, nullable=False)

class ErrorHistory(db.Model):
    __tablename__ = 'error_history'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=func.now())
    time = db.Column(db.Float, nullable=False)
    time_with_errors = db.Column(db.Float, nullable=False)
    error_1 = db.Column(db.Integer, nullable=False)
    error_2 = db.Column(db.Integer, nullable=False)
    error_3 = db.Column(db.Integer, nullable=False)
    error_4 = db.Column(db.Integer, nullable=False)
    error_5 = db.Column(db.Integer, nullable=False)
    error_6 = db.Column(db.Integer, nullable=False)
    error_7 = db.Column(db.Integer, nullable=False)
    error_8 = db.Column(db.Integer, nullable=False)
    error_9 = db.Column(db.Integer, nullable=False)
    error_10 = db.Column(db.Integer, nullable=False)
    error_11 = db.Column(db.Integer, nullable=False)
    error_12 = db.Column(db.Integer, nullable=False)
    error_13 = db.Column(db.Integer, nullable=False)
    error_14 = db.Column(db.Integer, nullable=False)
    error_15 = db.Column(db.Integer, nullable=False)
    error_16 = db.Column(db.Integer, nullable=False)


