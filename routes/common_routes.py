from flask import Blueprint, redirect, url_for, session, request
from models.notification import Notification
from models import db
from utils.decorators import login_required

common = Blueprint('common', __name__)

@common.route('/')
def index():
    """Redirect root to login or appropriate dashboard."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    role = session.get('role')
    if role == 'ADMIN':
        return redirect(url_for('admin.dashboard'))
    elif role == 'CLIENT':
        return redirect(url_for('client.dashboard'))
    else:
        return redirect(url_for('freelancer.dashboard'))

@common.route('/notifications/mark-read/<int:nid>')
@login_required
def mark_notification_read(nid):
    """Mark a single notification as READ."""
    n = Notification.query.get_or_404(nid)
    n.status = 'READ'
    db.session.commit()
    # Go back to wherever the user was
    return redirect(request.referrer or url_for('common.index'))

@common.route('/notifications/mark-all-read')
@login_required
def mark_all_read():
    """Mark all notifications for current user as READ."""
    Notification.query.filter_by(
        user_id=session['user_id'], status='UNREAD'
    ).update({'status': 'READ'})
    db.session.commit()
    return redirect(request.referrer or url_for('common.index'))
