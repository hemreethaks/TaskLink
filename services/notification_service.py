from models import db
from models.notification import Notification
from models.task import Task
from models.assignment import Assignment
from datetime import datetime, timedelta

def send_notification(user_id, message):
    """Create a new unread notification for a user."""
    n = Notification(user_id=user_id, message=message)
    db.session.add(n)
    db.session.commit()

def check_deadline_notifications():
    """
    Check tasks that have a deadline within the next 1 hour.
    If no notification has been sent yet, create one.
    Called when dashboards load – keeps it simple.
    """
    now   = datetime.now()
    soon  = now + timedelta(hours=1)

    # Tasks that are ASSIGNED and deadline is between now and 1 hr from now
    upcoming = Task.query.filter(
        Task.status == 'ASSIGNED',
        Task.deadline >= now,
        Task.deadline <= soon
    ).all()

    for task in upcoming:
        # Notify the assigned freelancer
        assignment = Assignment.query.filter_by(task_id=task.task_id).first()
        if assignment:
            msg = f"⏰ Pending: Deadline approaching for task '{task.title}' (due {task.deadline.strftime('%Y-%m-%d %H:%M')})"
            # Avoid duplicate notifications
            existing = Notification.query.filter_by(
                user_id=assignment.freelancer_id,
                message=msg
            ).first()
            if not existing:
                send_notification(assignment.freelancer_id, msg)

        # Also notify the client
        msg_client = f"⏰ Pending: Task '{task.title}' deadline is approaching!"
        existing_c = Notification.query.filter_by(
            user_id=task.client_id,
            message=msg_client
        ).first()
        if not existing_c:
            send_notification(task.client_id, msg_client)
