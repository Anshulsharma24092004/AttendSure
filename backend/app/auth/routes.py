from flask import request, jsonify, session
from . import auth_bp
from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get("role", "student")

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if role not in ["student", "teacher"]:
        return jsonify({"error": "Invalid role"}), 400

    # 1. Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # 2. Create new user
    user = User(
        name=name,
        email=email,
        role=role,
        is_active=True
    )
    user.set_password(password)

    # 3. Add to DB
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Signup successful"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # 1. Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    # 2. Verify password
    if not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # 3. Check if active
    if not user.is_active:
        return jsonify({"error": "Account inactive"}), 403

    # 4. Create session
    session['user_id'] = user.id
    session['role'] = user.role

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()  # destroys all session data
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }), 200
