# backend/models/db_setup.py
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def init_db(app: Flask):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    instance_dir = os.path.join(base_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(instance_dir, 'parking_app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        # Import all models so relationships resolve before mapper configuration
        from .User import User  # noqa: F401
        from .Reservation import Reservation  # noqa: F401
        from .ParkingSpot import ParkingSpot  # noqa: F401
        from .ParkingLot import ParkingLot  # noqa: F401
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
