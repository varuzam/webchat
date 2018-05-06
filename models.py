from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from typing import Dict, List

db = SQLAlchemy()

# a mock set which stores all chat messages ({room_id: [{user:, msg:, time:}, ..]}). It should be stored in DB
msg_history: Dict[int, List[Dict]] = {}

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True, nullable=False)
    password = db.Column(db.String(20))
    email = db.Column(db.String(30), unique=True, index=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    chatrooms = db.relationship('ChatRoom', backref='user', lazy='dynamic')

    @property
    def is_active(self):
        return self.active

    def __repr__(self):
        return '<User %r>' % (self.username)

class ChatRoom(db.Model):
    __tablename__ = "chatrooms"
    id: int = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, index=True, nullable=False)
    desc = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Chatroom %r>' % self.name
