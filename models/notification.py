from models import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message         = db.Column(db.String(500), nullable=False)
    status          = db.Column(db.Enum('UNREAD','READ'), default='UNREAD')
    created_at      = db.Column(db.DateTime, default=datetime.now)
