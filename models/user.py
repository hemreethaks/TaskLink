from models import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    user_id    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role       = db.Column(db.Enum('ADMIN', 'CLIENT', 'FREELANCER'), nullable=False)
    rating     = db.Column(db.Float, default=0.0)
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    tasks_posted   = db.relationship('Task',         foreign_keys='Task.client_id',       backref='client',     lazy=True)
    applications   = db.relationship('Application',  foreign_keys='Application.freelancer_id', backref='freelancer', lazy=True)
    notifications  = db.relationship('Notification', backref='user', lazy=True)
    activity_logs  = db.relationship('ActivityLog',  backref='user', lazy=True)
    monthly_reports= db.relationship('MonthlyReport',backref='user', lazy=True)
