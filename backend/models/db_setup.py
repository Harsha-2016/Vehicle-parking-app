# backend/models/db_setup.py
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        from .User import User  # import here to avoid circular imports
        db.create_all()

        # ✅ Ensure admin exists
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
                username="admin",
                password=generate_password_hash("admin123"),  # default password
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created with username=admin and password=admin123")
