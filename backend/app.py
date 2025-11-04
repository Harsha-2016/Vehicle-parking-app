# backend/app.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models.db_setup import init_db
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
import os 
from dotenv import load_dotenv
from extensions import cache

app = Flask(__name__)
"""Allow frontend (Vite default at 5173) to call the API during local dev."""
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
load_dotenv()

# 🔧 Redis cache configuration
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache timeout in seconds (5 mins)



# Secret key for JWT
app.config["JWT_SECRET_KEY"] = os.environ.get("SECRET_KEY")
jwt = JWTManager(app)

# Initialize Cache
cache.init_app(app)

# Init DB
init_db(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(user_bp, url_prefix="/user")

if __name__ == "__main__":
    app.run(debug=True)
