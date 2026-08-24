from models import db
from models.activity_log import ActivityLog
from datetime import datetime

def log_action(user_id, action, task_id=None):
    """Insert a row into activity_logs."""
    entry = ActivityLog(
        user_id=user_id,
        task_id=task_id,
        action=action,
        log_date=datetime.now()
    )
    db.session.add(entry)
    db.session.commit()
