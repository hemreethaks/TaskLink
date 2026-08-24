from models import db
from datetime import datetime

class Submission(db.Model):
    __tablename__ = 'submissions'

    submission_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id         = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    freelancer_id   = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    file_url        = db.Column(db.String(500), nullable=False)
    submission_note = db.Column(db.Text)
    submission_date = db.Column(db.DateTime, default=datetime.now)

    freelancer = db.relationship('User', foreign_keys=[freelancer_id])
