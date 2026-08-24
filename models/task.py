from models import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'

    task_id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id     = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    category_id   = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text, nullable=False)
    workload_level= db.Column(db.Enum('LOW','MEDIUM','HIGH'), nullable=False)
    budget        = db.Column(db.Float, nullable=False)
    deadline      = db.Column(db.DateTime, nullable=False)
    status        = db.Column(db.Enum('OPEN','ASSIGNED','SUBMITTED','COMPLETED','CANCELLED'), default='OPEN')
    created_at    = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    applications = db.relationship('Application',  backref='task', lazy=True, cascade='all, delete-orphan')
    assignments  = db.relationship('Assignment',   backref='task', lazy=True, cascade='all, delete-orphan')
    submissions  = db.relationship('Submission',   backref='task', lazy=True, cascade='all, delete-orphan')
    payments     = db.relationship('Payment',      backref='task', lazy=True)
    reviews      = db.relationship('Review',       backref='task', lazy=True)
    logs         = db.relationship('ActivityLog',  backref='task', lazy=True)
