from flask import Blueprint, render_template, redirect, url_for, flash, session
from models import db
from models.user import User
from models.task import Task
from models.payment import Payment
from models.activity_log import ActivityLog
from models.monthly_report import MonthlyReport
from utils.decorators import role_required
from utils.helpers import get_unread_notifications, get_unread_count

admin = Blueprint('admin', __name__, url_prefix='/admin')

# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@admin.route('/dashboard')
@role_required('ADMIN')
def dashboard():
    total_users     = User.query.count()
    total_tasks     = Task.query.count()
    open_tasks      = Task.query.filter_by(status='OPEN').count()
    completed_tasks = Task.query.filter_by(status='COMPLETED').count()
    total_payments  = Payment.query.filter_by(payment_status='RELEASED').count()

    uid = session['user_id']
    notifications  = get_unread_notifications(uid)
    notif_count    = get_unread_count(uid)

    return render_template('admin/dashboard.html',
        total_users=total_users,
        total_tasks=total_tasks,
        open_tasks=open_tasks,
        completed_tasks=completed_tasks,
        total_payments=total_payments,
        notifications=notifications,
        notif_count=notif_count
    )

# ─── USERS ────────────────────────────────────────────────────────────────────
@admin.route('/users')
@role_required('ADMIN')
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    uid = session['user_id']
    return render_template('admin/users.html',
        users=all_users,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )

@admin.route('/users/toggle/<int:user_id>')
@role_required('ADMIN')
def toggle_user(user_id):
    """Activate or deactivate a user account."""
    user = User.query.get_or_404(user_id)
    if user.role == 'ADMIN':
        flash('Cannot deactivate admin account.', 'warning')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.name} has been {status}.', 'success')
    return redirect(url_for('admin.users'))

# ─── TASKS ────────────────────────────────────────────────────────────────────
@admin.route('/tasks')
@role_required('ADMIN')
def tasks():
    all_tasks = Task.query.order_by(Task.created_at.desc()).all()
    uid = session['user_id']
    return render_template('admin/tasks.html',
        tasks=all_tasks,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )

@admin.route('/tasks/delete/<int:task_id>')
@role_required('ADMIN')
def delete_task(task_id):
    """Remove a fraudulent or cancelled task."""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task removed successfully.', 'success')
    return redirect(url_for('admin.tasks'))

# ─── PAYMENTS ─────────────────────────────────────────────────────────────────
@admin.route('/payments')
@role_required('ADMIN')
def payments():
    all_payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    uid = session['user_id']
    return render_template('admin/payments.html',
        payments=all_payments,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )

# ─── ACTIVITY LOGS ────────────────────────────────────────────────────────────
@admin.route('/logs')
@role_required('ADMIN')
def logs():
    all_logs = ActivityLog.query.order_by(ActivityLog.log_date.desc()).limit(200).all()
    uid = session['user_id']
    return render_template('admin/logs.html',
        logs=all_logs,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )

# ─── MONTHLY REPORTS ──────────────────────────────────────────────────────────
@admin.route('/reports')
@role_required('ADMIN')
def reports():
    all_reports = MonthlyReport.query.order_by(
        MonthlyReport.report_month.desc()
    ).all()
    uid = session['user_id']
    return render_template('admin/reports.html',
        reports=all_reports,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )
