from models import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'

    review_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id     = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating      = db.Column(db.Integer, nullable=False)   # 1–5
    comments    = db.Column(db.Text)
    review_date = db.Column(db.DateTime, default=datetime.now)

    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    reviewee = db.relationship('User', foreign_keys=[reviewee_id])
