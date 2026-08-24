from models import db

class MonthlyReport(db.Model):
    __tablename__ = 'monthly_reports'

    report_id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    report_month    = db.Column(db.String(7), nullable=False)   # e.g. "2024-04"
    total_tasks     = db.Column(db.Integer, default=0)
    completed_tasks = db.Column(db.Integer, default=0)
    active_tasks    = db.Column(db.Integer, default=0)
    total_earnings  = db.Column(db.Float, default=0.0)
