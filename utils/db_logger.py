"""
db_logger.py
Thin wrapper so route files can call one function instead of importing
both activity_service and the session user_id every time.
"""
from flask import session
from services.activity_service import log_action as _log

def log(action, task_id=None):
    user_id = session.get('user_id')
    if user_id:
        _log(user_id, action, task_id)
