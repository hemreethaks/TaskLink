from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models import db
from models.task import Task
from models.category import Category
from models.application import Application
from models.assignment import Assignment
from models.submission import Submission
from models.review import Review
from models.user import User
from services.notification_service import send_notification, check_deadline_notifications
from services.payment_service import release_payment as process_payment
from services.activity_service import log_action
from utils.decorators import role_required
from utils.helpers import get_unread_notifications, get_unread_count
from utils.db_logger import log

client = Blueprint('client', __name__, url_prefix='/client')


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@client.route('/dashboard')
@role_required('CLIENT')
def dashboard():
    uid = session['user_id']
    check_deadline_notifications()

    my_tasks = Task.query.filter_by(client_id=uid).count()
    open_tasks = Task.query.filter_by(client_id=uid, status='OPEN').count()
    assigned = Task.query.filter_by(client_id=uid, status='ASSIGNED').count()
    completed = Task.query.filter_by(client_id=uid, status='COMPLETED').count()
    recent_tasks = Task.query.filter_by(client_id=uid).order_by(Task.created_at.desc()).limit(5).all()

    return render_template(
        'client/dashboard.html',
        my_tasks=my_tasks,
        open_tasks=open_tasks,
        assigned=assigned,
        completed=completed,
        recent_tasks=recent_tasks,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── CREATE TASK ──────────────────────────────────────────────────────────────
@client.route('/create-task', methods=['GET', 'POST'])
@role_required('CLIENT')
def create_task():
    categories = Category.query.all()
    uid = session['user_id']

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id')
        workload_level = request.form.get('workload_level')
        budget = request.form.get('budget')
        deadline_str = request.form.get('deadline')

        if not all([title, description, category_id, workload_level, budget, deadline_str]):
            flash('Please fill all fields.', 'danger')
            return redirect(url_for('client.create_task'))

        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid deadline format.', 'danger')
            return redirect(url_for('client.create_task'))

        task = Task(
            client_id=uid,
            category_id=int(category_id),
            title=title,
            description=description,
            workload_level=workload_level,
            budget=float(budget),
            deadline=deadline,
            status='OPEN'
        )
        db.session.add(task)
        db.session.commit()

        log('Posted new task: ' + title, task.task_id)
        flash('Task posted successfully!', 'success')
        return redirect(url_for('client.my_tasks'))

    return render_template(
        'client/create_task.html',
        categories=categories,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── MY TASKS ─────────────────────────────────────────────────────────────────
@client.route('/my-tasks')
@role_required('CLIENT')
def my_tasks():
    uid = session['user_id']
    tasks = Task.query.filter_by(client_id=uid).order_by(Task.created_at.desc()).all()

    return render_template(
        'client/my_tasks.html',
        tasks=tasks,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── CANCEL TASK ──────────────────────────────────────────────────────────────
@client.route('/cancel-task/<int:task_id>')
@role_required('CLIENT')
def cancel_task(task_id):
    uid = session['user_id']
    task = Task.query.get_or_404(task_id)

    if task.client_id != uid:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('client.my_tasks'))

    if task.status not in ('OPEN', 'ASSIGNED'):
        flash('Cannot cancel this task.', 'warning')
        return redirect(url_for('client.my_tasks'))

    task.status = 'CANCELLED'
    db.session.commit()

    log('Cancelled task: ' + task.title, task_id)
    flash('Task cancelled.', 'info')
    return redirect(url_for('client.my_tasks'))


# ─── VIEW APPLICATIONS ────────────────────────────────────────────────────────
@client.route('/task-applications/<int:task_id>')
@role_required('CLIENT')
def task_applications(task_id):
    uid = session['user_id']
    task = Task.query.get_or_404(task_id)

    if task.client_id != uid:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('client.my_tasks'))

    applications = Application.query.filter_by(task_id=task_id).all()
    assignment = Assignment.query.filter_by(task_id=task_id).first()
    submission = Submission.query.filter_by(task_id=task_id).first()

    return render_template(
        'client/task_applications.html',
        task=task,
        applications=applications,
        assignment=assignment,
        submission=submission,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── ASSIGN FREELANCER ────────────────────────────────────────────────────────
@client.route('/assign/<int:task_id>/<int:freelancer_id>')
@role_required('CLIENT')
def assign_freelancer(task_id, freelancer_id):
    uid = session['user_id']
    task = Task.query.get_or_404(task_id)

    if task.client_id != uid:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('client.my_tasks'))

    if task.status != 'OPEN':
        flash('Task is not open for assignment.', 'warning')
        return redirect(url_for('client.task_applications', task_id=task_id))

    assignment = Assignment(task_id=task_id, freelancer_id=freelancer_id)
    db.session.add(assignment)

    task.status = 'ASSIGNED'
    db.session.commit()

    freelancer = User.query.get(freelancer_id)
    send_notification(freelancer_id, f"🎉 You have been assigned to task: '{task.title}'!")

    log_action(uid, f"Assigned task '{task.title}' to {freelancer.name}", task_id)

    from services.report_service import increment_active_task
    increment_active_task(freelancer_id)

    flash(f'{freelancer.name} has been assigned to the task!', 'success')
    return redirect(url_for('client.task_applications', task_id=task_id))


# ─── APPROVE SUBMISSION ───────────────────────────────────────────────────────
@client.route('/approve/<int:task_id>')
@role_required('CLIENT')
def approve_submission(task_id):
    uid = session['user_id']
    task = Task.query.get_or_404(task_id)

    if task.client_id != uid:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('client.my_tasks'))

    if task.status != 'SUBMITTED':
        flash('No submission to approve yet.', 'warning')
        return redirect(url_for('client.task_applications', task_id=task_id))

    task.status = 'COMPLETED'
    db.session.commit()

    log(f"Approved submission for task '{task.title}'", task_id)

    flash('Submission approved! You can now release payment.', 'success')
    return redirect(url_for('client.release_payment', task_id=task_id))


# ─── RELEASE PAYMENT ──────────────────────────────────────────────────────────
@client.route('/release-payment/<int:task_id>', methods=['GET', 'POST'])
@role_required('CLIENT')
def release_payment(task_id):
    uid = session['user_id']
    task = Task.query.get_or_404(task_id)
    assignment = Assignment.query.filter_by(task_id=task_id).first()

    if not assignment:
        flash('No assignment found.', 'danger')
        return redirect(url_for('client.my_tasks'))

    if request.method == 'POST':
        success, result = process_payment(task_id, uid, assignment.freelancer_id)

        if success:
            flash(f'Payment of ₹{result} released successfully!', 'success')
            return redirect(url_for('client.add_review', task_id=task_id))
        else:
            flash(f'Payment error: {result}', 'danger')

    from services.payment_service import calculate_amount
    estimated = calculate_amount(task)

    return render_template(
        'client/release_payment.html',
        task=task,
        assignment=assignment,
        estimated=estimated,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )


# ─── ADD REVIEW ───────────────────────────────────────────────────────────────
@client.route('/add-review/<int:task_id>', methods=['GET', 'POST'])
@role_required('CLIENT')
def add_review(task_id):
    uid = session['user_id']
    task = Task.query.get_or_404(task_id)
    assignment = Assignment.query.filter_by(task_id=task_id).first()

    if not assignment:
        flash('No assignment for this task.', 'danger')
        return redirect(url_for('client.my_tasks'))

    existing_review = Review.query.filter_by(task_id=task_id, reviewer_id=uid).first()

    if request.method == 'POST':
        if existing_review:
            flash('You have already reviewed this task.', 'warning')
            return redirect(url_for('client.my_tasks'))

        rating = int(request.form.get('rating', 3))
        comments = request.form.get('comments', '').strip()

        review = Review(
            task_id=task_id,
            reviewer_id=uid,
            reviewee_id=assignment.freelancer_id,
            rating=rating,
            comments=comments
        )
        db.session.add(review)

        freelancer = User.query.get(assignment.freelancer_id)
        all_reviews = Review.query.filter_by(reviewee_id=assignment.freelancer_id).all()
        total_rating = sum(r.rating for r in all_reviews) + rating
        freelancer.rating = round(total_rating / (len(all_reviews) + 1), 2)

        db.session.commit()
        log(f"Added review for task '{task.title}'", task_id)
        flash('Review submitted! Thank you.', 'success')
        return redirect(url_for('client.my_tasks'))

    return render_template(
        'client/add_review.html',
        task=task,
        assignment=assignment,
        existing_review=existing_review,
        notifications=get_unread_notifications(uid),
        notif_count=get_unread_count(uid)
    )