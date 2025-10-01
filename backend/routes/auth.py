# backend/routes/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.db_setup import db
from models.User import User

auth_bp = Blueprint('auth', __name__)

# --- User Registration ---
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400
    
    new_user = User(
        username=data['username'],
        password=generate_password_hash(data['password']),
        role="user"  # default role
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


# --- Login for both Admin and User ---
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Create JWT token
    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({
        "access_token": access_token,
        "role": user.role,
        "message": f"Welcome {user.role}"
    }), 200


# --- Protected Dashboard Example ---
@auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    current_user = get_jwt_identity()
    if current_user["role"] == "admin":
        return jsonify({"dashboard": "Admin Dashboard"}), 200
    return jsonify({"dashboard": "User Dashboard"}), 200
