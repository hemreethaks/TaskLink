from models import db
from models.monthly_report import MonthlyReport
from datetime import datetime

def update_monthly_report(freelancer_id, earnings=0.0):
    """
    Update (or create) the monthly report for a freelancer.
    Called after payment is released.
    """
    month_str = datetime.now().strftime('%Y-%m')   # e.g. "2024-04"

    report = MonthlyReport.query.filter_by(
        user_id=freelancer_id,
        report_month=month_str
    ).first()

    if report:
        report.completed_tasks += 1
        report.total_tasks     += 1
        report.total_earnings  += earnings
    else:
        report = MonthlyReport(
            user_id=freelancer_id,
            report_month=month_str,
            total_tasks=1,
            completed_tasks=1,
            active_tasks=0,
            total_earnings=earnings
        )
        db.session.add(report)

    db.session.commit()

def increment_active_task(freelancer_id):
    """Called when a freelancer is assigned a task."""
    month_str = datetime.now().strftime('%Y-%m')
    report = MonthlyReport.query.filter_by(
        user_id=freelancer_id,
        report_month=month_str
    ).first()

    if report:
        report.active_tasks += 1
        report.total_tasks  += 1
    else:
        report = MonthlyReport(
            user_id=freelancer_id,
            report_month=month_str,
            total_tasks=1,
            completed_tasks=0,
            active_tasks=1,
            total_earnings=0.0
        )
        db.session.add(report)

    db.session.commit()
