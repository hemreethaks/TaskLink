from models import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id        = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    client_id      = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    freelancer_id  = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    amount         = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.Enum('PENDING','RELEASED'), default='PENDING')
    payment_date   = db.Column(db.DateTime, default=datetime.now)

    client     = db.relationship('User', foreign_keys=[client_id])
    freelancer = db.relationship('User', foreign_keys=[freelancer_id])
