from models import db
from models.payment import Payment
from models.task import Task
from services.notification_service import send_notification
from services.activity_service import log_action
from services.report_service import update_monthly_report


# ─── CALCULATE AMOUNT (FINAL FIXED) ─────────────────────────────
def calculate_amount(task):
    """Return exact task budget (no multiplier)."""
    return round(task.budget, 2)


# ─── RELEASE PAYMENT ────────────────────────────────────────────
def release_payment(task_id, client_id, freelancer_id):
    """
    Release payment to freelancer.
    Uses a database transaction to ensure consistency.
    """
    try:
        task = Task.query.get(task_id)

        # Final amount = exact budget
        amount = calculate_amount(task)

        # Check if payment already exists
        payment = Payment.query.filter_by(task_id=task_id).first()

        if payment:
            payment.payment_status = 'RELEASED'
            payment.amount = amount
        else:
            payment = Payment(
                task_id=task_id,
                client_id=client_id,
                freelancer_id=freelancer_id,
                amount=amount,
                payment_status='RELEASED'
            )
            db.session.add(payment)

        # Update task status
        task.status = 'COMPLETED'

        db.session.commit()

        # Notify freelancer
        send_notification(
            freelancer_id,
            f"💰 Payment of ₹{amount} released for task '{task.title}'!"
        )

        # Log activity
        log_action(
            client_id,
            f"Released payment ₹{amount} for task '{task.title}'",
            task_id
        )

        # Update report
        update_monthly_report(freelancer_id, amount)

        return True, amount

    except Exception as e:
        db.session.rollback()
        return False, str(e)