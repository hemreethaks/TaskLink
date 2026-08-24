from models import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'applications'

    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id        = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    freelancer_id  = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    bid_amount     = db.Column(db.Float, nullable=False)
    proposal       = db.Column(db.Text, nullable=False)
    applied_date   = db.Column(db.DateTime, default=datetime.now)
