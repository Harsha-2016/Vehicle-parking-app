# backend/app.py
from flask import Flask
from backend.models.db_setup import db, jwt, cache, cors
from backend.routes.admin import admin_bp
from backend.routes.user import user_bp
from backend.routes.auth import auth_bp
from backend.models.User import User
from backend.models.Reservation import Reservation
from backend.models.ParkingLot import ParkingLot
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def create_app():
    app = Flask(__name__)
    base_dir = os.path.abspath(os.path.dirname(__file__))  # backend/
    db_path = os.path.join(base_dir, "..", "smart_parking.db")  # go one level up
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY',)
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    cors.init_app(app)

    # Register Blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Create database tables and default admin
    with app.app_context():
        db.create_all()

        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created (username: admin, password: admin123)")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
