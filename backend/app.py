# backend/app.py
from flask import Flask
from flask_jwt_extended import JWTManager
from models.db_setup import init_db
from routes.auth import auth_bp

app = Flask(__name__)

# Secret key for JWT
app.config["JWT_SECRET_KEY"] = "supersecretkey123"
jwt = JWTManager(app)

# Init DB
init_db(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run(debug=True)
