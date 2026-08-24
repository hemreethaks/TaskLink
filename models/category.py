from models import db

class Category(db.Model):
    __tablename__ = 'categories'

    category_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)

    tasks = db.relationship('Task', backref='category', lazy=True)
