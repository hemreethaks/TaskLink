from models import db
from datetime import datetime

class Assignment(db.Model):
    __tablename__ = 'assignments'

    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id       = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.now)

    freelancer = db.relationship('User', foreign_keys=[freelancer_id])
