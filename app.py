from flask import Flask
from config import Config
from models import db

# Import all models so SQLAlchemy knows about them
from models.user import User
from models.category import Category
from models.task import Task
from models.application import Application
from models.assignment import Assignment
from models.submission import Submission
from models.payment import Payment
from models.review import Review
from models.notification import Notification
from models.activity_log import ActivityLog
from models.monthly_report import MonthlyReport

# Import Blueprints
from routes.auth_routes      import auth
from routes.admin_routes     import admin
from routes.client_routes    import client
from routes.freelancer_routes import freelancer
from routes.common_routes    import common

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database with app
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(client)
    app.register_blueprint(freelancer)
    app.register_blueprint(common)

    # Make helpers available in all templates
    from utils.helpers import status_badge, get_unread_count
    app.jinja_env.globals['status_badge'] = status_badge

    return app


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # Create tables if they don't exist
    app.run(debug=True)
