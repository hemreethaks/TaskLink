from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from models import db
from models.task import Task
from models.category import Category
from models.application import Application
from models.assignment import Assignment
from models.submission import Submission
from models.payment import Payment
from models.review import Review
from models.monthly_report import MonthlyReport
from services.notification_service import send_notification, check_deadline_notifications
from services.activity_service import log_action
from utils.decorators import role_required
from utils.helpers import get_unread_notifications, get_unread_count
from utils.db_logger import log

freelancer = Blueprint('freelancer', __name__, url_prefix='/freelancer')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'zip', 'png', 'jpg', 'jpeg', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@freelancer.route('/dashboard')
@role_required('FREELANCER')
def dashboard():
    uid = session['user_id']
    check_deadline_notifications()

    applied       = Application.query.filter_by(freelancer_id=uid).count()
    assigned      = Assignment.query.filter_by(freelancer_id=uid).count()
    completed     = Payment.query.filter_by(freelancer_id=uid, payment_status='RELEASED').count()
    total_earned  = db.session.query(db.func.sum(Payment.amount)).filter_by(
                        freelancer_id=uid, payment_status='RELEASED').scalar() or 0

    # Recent assigned tasks
    assigned_task_ids = [a.task_id for a in Assignment.query.filter_by(freelancer_id=uid).all()]
    recent_tasks = Task.query.filter(Task.task_id.in_(assigned_task_ids))\
                             .order_by(Task.created_at.desc()).limit(5).all()

    return render_template('freelancer/dashboard.html',
        applied=applied, assigned=assigned,
        completed=completed, total_earned=total_earned,
        recent_tasks=recent_tasks,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── BROWSE OPEN TASKS ────────────────────────────────────────────────────────
@freelancer.route('/browse-tasks')
@role_required('FREELANCER')
def browse_tasks():
    uid         = session['user_id']
    category_id = request.args.get('category_id', type=int)
    categories  = Category.query.all()

    query = Task.query.filter_by(status='OPEN')
    if category_id:
        query = query.filter_by(category_id=category_id)

    tasks = query.order_by(Task.created_at.desc()).all()

    # Find tasks this freelancer has already applied to
    applied_task_ids = {a.task_id for a in Application.query.filter_by(freelancer_id=uid).all()}

    return render_template('freelancer/browse_tasks.html',
        tasks=tasks,
        categories=categories,
        applied_task_ids=applied_task_ids,
        selected_cat=category_id,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── APPLY FOR TASK ───────────────────────────────────────────────────────────
@freelancer.route('/apply/<int:task_id>', methods=['GET', 'POST'])
@role_required('FREELANCER')
def apply_task(task_id):
    uid  = session['user_id']
    task = Task.query.get_or_404(task_id)

    if task.status != 'OPEN':
        flash('This task is no longer open.', 'warning')
        return redirect(url_for('freelancer.browse_tasks'))

    # Prevent duplicate applications
    already_applied = Application.query.filter_by(
        task_id=task_id, freelancer_id=uid
    ).first()
    if already_applied:
        flash('You have already applied for this task.', 'warning')
        return redirect(url_for('freelancer.browse_tasks'))

    if request.method == 'POST':
        bid_amount = request.form.get('bid_amount')
        proposal   = request.form.get('proposal', '').strip()

        if not bid_amount or not proposal:
            flash('Please fill all fields.', 'danger')
            return redirect(url_for('freelancer.apply_task', task_id=task_id))

        application = Application(
            task_id       = task_id,
            freelancer_id = uid,
            bid_amount    = float(bid_amount),
            proposal      = proposal
        )
        db.session.add(application)
        db.session.commit()

        log(f"Applied for task '{task.title}'", task_id)
        # Notify the client
        send_notification(task.client_id,
            f"📩 New application received for your task '{task.title}'!")

        flash('Application submitted successfully!', 'success')
        return redirect(url_for('freelancer.browse_tasks'))

    return render_template('freelancer/apply_task.html',
        task=task,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── ASSIGNED TASKS ───────────────────────────────────────────────────────────
@freelancer.route('/assigned-tasks')
@role_required('FREELANCER')
def assigned_tasks():
    uid         = session['user_id']
    assignments = Assignment.query.filter_by(freelancer_id=uid).all()
    task_ids    = [a.task_id for a in assignments]
    tasks       = Task.query.filter(Task.task_id.in_(task_ids)).all()

    # Map task_id -> submission for quick lookup in template
    submission_map = {
        s.task_id: s for s in Submission.query.filter_by(freelancer_id=uid).all()
    }

    return render_template('freelancer/assigned_tasks.html',
        tasks=tasks,
        submission_map=submission_map,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── SUBMIT WORK ──────────────────────────────────────────────────────────────
@freelancer.route('/submit-work/<int:task_id>', methods=['GET', 'POST'])
@role_required('FREELANCER')
def submit_work(task_id):
    uid  = session['user_id']
    task = Task.query.get_or_404(task_id)

    # Verify this freelancer is assigned
    assignment = Assignment.query.filter_by(task_id=task_id, freelancer_id=uid).first()
    if not assignment:
        flash('You are not assigned to this task.', 'danger')
        return redirect(url_for('freelancer.assigned_tasks'))

    # Check if already submitted
    existing = Submission.query.filter_by(task_id=task_id, freelancer_id=uid).first()
    if existing:
        flash('You have already submitted work for this task.', 'info')
        return redirect(url_for('freelancer.assigned_tasks'))

    if request.method == 'POST':
        file_url        = request.form.get('file_url', '').strip()
        submission_note = request.form.get('submission_note', '').strip()
        upload_file     = request.files.get('upload_file')

        # Handle uploaded file
        if upload_file and upload_file.filename and allowed_file(upload_file.filename):
            filename = secure_filename(upload_file.filename)
            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            upload_file.save(save_path)
            file_url = f'/static/uploads/{filename}'

        if not file_url:
            flash('Please upload a file or provide a link.', 'danger')
            return redirect(url_for('freelancer.submit_work', task_id=task_id))

        submission = Submission(
            task_id         = task_id,
            freelancer_id   = uid,
            file_url        = file_url,
            submission_note = submission_note
        )
        db.session.add(submission)
        task.status = 'SUBMITTED'
        db.session.commit()

        log(f"Submitted work for task '{task.title}'", task_id)
        # Notify the client
        send_notification(task.client_id,
            f"✅ Freelancer has submitted work for task '{task.title}'. Please review!")

        flash('Work submitted successfully!', 'success')
        return redirect(url_for('freelancer.assigned_tasks'))

    return render_template('freelancer/submit_work.html',
        task=task,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── PAYMENT HISTORY ──────────────────────────────────────────────────────────
@freelancer.route('/payments')
@role_required('FREELANCER')
def payments():
    uid      = session['user_id']
    payments = Payment.query.filter_by(freelancer_id=uid)\
                            .order_by(Payment.payment_date.desc()).all()
    return render_template('freelancer/payments.html',
        payments=payments,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── MONTHLY REPORT ───────────────────────────────────────────────────────────
@freelancer.route('/reports')
@role_required('FREELANCER')
def reports():
    uid     = session['user_id']
    reports = MonthlyReport.query.filter_by(user_id=uid)\
                                 .order_by(MonthlyReport.report_month.desc()).all()
    reviews = Review.query.filter_by(reviewee_id=uid).all()

    return render_template('freelancer/reports.html',
        reports=reports,
        reviews=reviews,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )
