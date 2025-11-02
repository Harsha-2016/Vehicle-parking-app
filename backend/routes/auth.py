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
    # Accept JSON or form-encoded bodies
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        data = request.form.to_dict()

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    # frontend sends email but our model doesn't store it; ignore safely

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    try:
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role="user"
        )
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed", "detail": str(e)}), 500

    return jsonify({"message": "User registered successfully"}), 201


# --- Login for both Admin and User ---
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    print(f"DEBUG: Login attempt for username: {data.get('username')}")
    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password, data['password']):
        print(f"DEBUG: Login failed for user: {data.get('username')}")
        return jsonify({"error": "Invalid username or password"}), 401

    # ✅ FIX: identity must be a string
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    print(f"DEBUG: Login successful for user: {user.username}, role: {user.role}")
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
