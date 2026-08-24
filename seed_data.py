"""
seed_data.py
Run this ONCE after setting up the database to populate sample data.

Usage:
    python seed_data.py
"""

from app import app
from models import db
from models.user import User
from models.category import Category
from models.task import Task
from models.application import Application
from models.assignment import Assignment
from models.submission import Submission
from models.payment import Payment
from models.review import Review
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def seed():
    with app.app_context():
        db.create_all()

        # ── Categories ──────────────────────────────────────
        categories = [
            'Data Entry', 'Logo Design', 'Code Debugging',
            'Translation', 'Writing', 'Resume Review',
            'PPT Creation', 'Research Work', 'Others'
        ]
        cat_objects = []
        for name in categories:
            c = Category.query.filter_by(category_name=name).first()
            if not c:
                c = Category(category_name=name)
                db.session.add(c)
            cat_objects.append(c)
        db.session.commit()
        print("✅ Categories seeded.")

        # ── Admin ────────────────────────────────────────────
        if not User.query.filter_by(email='admin@gmail.com').first():
            admin = User(
                name          = 'Admin',
                email         = 'admin@gmail.com',
                password_hash = generate_password_hash('tl@admin'),
                role          = 'ADMIN',
                is_active     = True
            )
            db.session.add(admin)

        # ── Sample Clients ────────────────────────────────────
        clients_data = [
            ('caira@gmail.com', 'caira@pass',  'Caira John'),
            ('nithya@gmail.com',  'nithya@pass',  'Nithya Chandran'),
            ('anjana@gmail.com',  'anjana@pass',  'Anjana Ragav'),
            ('rithik@gmail.com',  'rithik@pass',  'Rithik Krishna')
        ]
        client_objs = []
        for email, pwd, name in clients_data:
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(
                    name          = name,
                    email         = email,
                    password_hash = generate_password_hash(pwd),
                    role          = 'CLIENT',
                    is_active     = True
                )
                db.session.add(u)
                print(f"✅ Client created → {email}")
            client_objs.append(u)

        # ── Sample Freelancers ─────────────────────────────────
        freelancers_data = [
            ('karthi@gmail.com',  'karthi@pass',  'Karthikeyan',    4.5),
            ('deeps@gmail.com', 'deeps@pass',  'Deeps',   4.2),
            ('aadhavan@gmail.com', 'aadhavan@pass',  'Aadhavan',  4.6),
            ('vicky@gmail.com', 'vicky@pass',  'Vicky',     3.9),
            ('akilesh@gmail.com', 'akilesh@pass',  'Akilesh',    4.8),
        ]
        freelancer_objs = []
        for email, pwd, name, rating in freelancers_data:
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(
                    name          = name,
                    email         = email,
                    password_hash = generate_password_hash(pwd),
                    role          = 'FREELANCER',
                    rating        = rating,
                    is_active     = True
                )
                db.session.add(u)
                print(f"✅ Freelancer created → {email}")
            freelancer_objs.append(u)

        db.session.commit()

        # ── Refresh objects after commit ──
        for i, (email, _, _) in enumerate(clients_data):
            client_objs[i] = User.query.filter_by(email=email).first()
        for i, (email, _, _, _) in enumerate(freelancers_data):
            freelancer_objs[i] = User.query.filter_by(email=email).first()

        # ── Categories refresh ──
        cat_map = {c.category_name: c for c in Category.query.all()}

        # ── Sample Tasks ───────────────────────────────────────
        tasks_data = [
            (client_objs[0], 'Design a Logo for My Bakery',
             'Need a clean, modern logo for my new bakery brand. Prefer warm colors like orange and brown.',
             'Logo Design', 500, 'MEDIUM', 'OPEN', 5),
            (client_objs[0], 'Fix Python Flask Bug',
             'My Flask app crashes on login. Need someone to debug the auth module and fix the issue.',
             'Code Debugging', 800, 'HIGH', 'OPEN', 3),
            (client_objs[1], 'Translate Tamil Article to English',
             'I have a 1500-word Tamil article about agriculture that needs to be translated to English accurately.',
             'Translation', 400, 'LOW', 'OPEN', 7),
            (client_objs[1], 'Create a Sales PPT',
             'Need a 10-slide PowerPoint presentation for our quarterly sales meeting. Include charts and graphs.',
             'PPT Creation', 600, 'MEDIUM', 'OPEN', 2),
            (client_objs[2], 'Data Entry - Student Records',
             'Enter 200 student records from scanned sheets into an Excel file. Clean and formatted output expected.',
             'Data Entry', 300, 'LOW', 'COMPLETED', 10),
            (client_objs[2], 'Write Blog Posts on Technology',
             'Need 5 blog posts (500 words each) on topics like AI, cloud computing, and cybersecurity.',
             'Writing', 1000, 'HIGH', 'OPEN', 4),
            (client_objs[0], 'Resume Review and Improvement',
             'I am a fresher looking for my first IT job. Please review and improve my resume for better chances.',
             'Resume Review', 250, 'LOW', 'OPEN', 6),
            (client_objs[1], 'Research on Electric Vehicles in India',
             'Collect data and write a 2000-word research summary on EV adoption trends in India for 2024-2025.',
             'Research Work', 700, 'MEDIUM', 'OPEN', 5),
        ]

        created_tasks = []
        for i, (client, title, desc, cat_name, budget, workload, status, days_ahead) in enumerate(tasks_data):
            if not Task.query.filter_by(title=title).first():
                t = Task(
                    client_id    = client.user_id,
                    category_id  = cat_map[cat_name].category_id,
                    title        = title,
                    description  = desc,
                    budget       = budget,
                    workload_level = workload,
                    status       = status,
                    deadline     = datetime.now() + timedelta(days=days_ahead)
                )
                db.session.add(t)
                created_tasks.append((t, status))
                print(f"✅ Task created: {title}")
        db.session.commit()


if __name__ == '__main__':
    seed()
