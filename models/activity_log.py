from models import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    log_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    task_id  = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=True)
    action   = db.Column(db.String(300), nullable=False)
    log_date = db.Column(db.DateTime, default=datetime.now)
