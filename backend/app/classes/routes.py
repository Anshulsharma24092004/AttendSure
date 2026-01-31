from flask import request, jsonify, session
from app.models.class_model import Class
from app.models.enrollment import Enrollment
from app.extensions import db
from . import classes_bp


@classes_bp.route("", methods=["POST"])
def create_class():
    # 1. Must be logged in
    user_id = session.get("user_id")
    role = session.get("role")

    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    # 2. Must be a teacher
    if role != "teacher":
        return jsonify({"error": "Only teachers can create classes"}), 403

    data = request.get_json()

    name = data.get("name")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    radius_meters = data.get("radius_meters")

    if not name:
        return jsonify({"error": "Class name is required"}), 400
    
    if latitude is None or longitude is None or radius_meters is None:
        return jsonify({"error": "latitude, longitude, radius_meters are required"}), 400

    # 3. Create class
    new_class = Class(
        name=name,
        teacher_id=user_id,
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius_meters,
        is_active=True
    )

    db.session.add(new_class)
    db.session.commit()

    return jsonify({
        "message": "Class created successfully",
        "class_id": new_class.id
    }), 201


@classes_bp.route("/<int:class_id>/enroll", methods=["POST"])
def enroll_in_class(class_id):
    # Must be logged in
    user_id = session.get("user_id")
    role = session.get("role")

    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    # Must be a student
    if role != "student":
        return jsonify({"error": "Only students can enroll"}), 403

    # Check class exists
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404

    # Already enrolled?
    existing = Enrollment.query.filter_by(
        student_id=user_id,
        class_id=class_id
    ).first()

    if existing:
        return jsonify({"message": "Already enrolled", "class_id": class_id}), 200

    enrollment = Enrollment(student_id=user_id, class_id=class_id)
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({"message": "Enrolled successfully", "class_id": class_id}), 201


@classes_bp.route("", methods=["GET"])
def list_classes():
    user_id = session.get("user_id")
    role = session.get("role")

    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    # Teacher: classes they created
    if role == "teacher":
        classes = Class.query.filter_by(teacher_id=user_id).all()

        return jsonify({
            "classes": [
                {
                    "id": c.id,
                    "name": c.name,
                    "teacher_id": c.teacher_id,
                    "latitude": float(c.latitude),
                    "longitude": float(c.longitude),
                    "radius_meters": float(c.radius_meters),
                    "is_active": bool(c.is_active)
                }
                for c in classes
            ]
        }), 200

    # Student: classes they enrolled in
    elif role == "student":
        enrollments = Enrollment.query.filter_by(student_id=user_id).all()
        class_ids = [e.class_id for e in enrollments]

        if not class_ids:
            return jsonify({"classes": []}), 200

        classes = Class.query.filter(Class.id.in_(class_ids)).all()

        return jsonify({
            "classes": [
                {
                    "id": c.id,
                    "name": c.name,
                    "teacher_id": c.teacher_id,
                    "latitude": float(c.latitude),
                    "longitude": float(c.longitude),
                    "radius_meters": float(c.radius_meters),
                    "is_active": bool(c.is_active)
                }
                for c in classes
            ]
        }), 200

    return jsonify({"error": "Invalid role"}), 400