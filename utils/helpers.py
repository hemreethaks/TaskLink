from models.notification import Notification

def get_unread_count(user_id):
    """Return number of unread notifications for sidebar badge."""
    return Notification.query.filter_by(user_id=user_id, status='UNREAD').count()

def get_unread_notifications(user_id, limit=5):
    """Return latest unread notifications for dropdown."""
    return Notification.query.filter_by(user_id=user_id, status='UNREAD')\
                             .order_by(Notification.created_at.desc())\
                             .limit(limit).all()

def status_badge(status):
    """Return Bootstrap badge class for a given task/payment status."""
    mapping = {
        'OPEN':      'bg-success',
        'ASSIGNED':  'bg-primary',
        'SUBMITTED': 'bg-warning text-dark',
        'COMPLETED': 'bg-secondary',
        'CANCELLED': 'bg-danger',
        'PENDING':   'bg-warning text-dark',
        'RELEASED':  'bg-success',
        'UNREAD':    'bg-danger',
        'READ':      'bg-secondary',
    }
    return mapping.get(status, 'bg-dark')
