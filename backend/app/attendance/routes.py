from flask import request, jsonify, session
from . import attendance_bp
from app.models.user import User
from app.models.class_model import Class  # if needed
from app.models.enrollment import Enrollment
from app.models.attendance_session import AttendanceSession
from app.models.attendance_record import AttendanceRecord
from app.extensions import db
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
import hashlib

def distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def generate_device_hash(user_agent, screen_size, timezone, language, ip_subnet):
    hash_input = f"{user_agent}|{screen_size}|{timezone}|{language}|{ip_subnet}"
    return hashlib.sha256(hash_input.encode()).hexdigest()

@attendance_bp.route('/submit', methods=['POST'])
def submit_attendance():
    # 1️⃣ Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    if session.get("role") != "student":
        return jsonify({"error": "Only students can submit attendance"}), 403

    user_id = session['user_id']
    data = request.get_json()

    # 2️⃣ Extract request data
    session_id = data.get('attendance_session_id')
    submitted_lat = data.get('latitude')
    submitted_lon = data.get('longitude')
    attendance_code = data.get('attendance_code')

    if not session_id or attendance_code is None:
        return jsonify({"error": "attendance_session_id and attendance_code are required"}), 400

    # Device info from frontend
    device_info = data.get('device_info', {})
    user_agent = device_info.get('user_agent')
    screen_size = device_info.get('screen_size')
    timezone = device_info.get('timezone')
    language = device_info.get('language')
    ip_subnet = device_info.get('ip_subnet')

    # 3️⃣ Fetch attendance session
    attendance_session = AttendanceSession.query.get(session_id)
    if not attendance_session or not attendance_session.is_active:
        return jsonify({"error": "Attendance session not found or inactive"}), 404
    
    # Time window check (optional but good)
    #now = datetime.utcnow()
    #if getattr(attendance_session, "starts_at", None) and now < attendance_session.starts_at:
        #return jsonify({"error": "Attendance window not started"}), 400
    #if getattr(attendance_session, "ends_at", None) and now > attendance_session.ends_at:
        #return jsonify({"error": "Attendance window ended"}), 400
    

    now = datetime.now()  # ✅ local time (matches your Postman inputs)

    if getattr(attendance_session, "starts_at", None) and now < attendance_session.starts_at:
        return jsonify({
            "error": "Attendance window not started",
            "now": now.isoformat(),
            "starts_at": attendance_session.starts_at.isoformat() if attendance_session.starts_at else None
        }), 400

    if getattr(attendance_session, "ends_at", None) and now > attendance_session.ends_at:
        return jsonify({
            "error": "Attendance window ended",
            "now": now.isoformat(),
            "ends_at": attendance_session.ends_at.isoformat() if attendance_session.ends_at else None
        }), 400

    # 4️⃣ Check if student is enrolled in the class
    enrollment = Enrollment.query.filter_by(
        student_id=user_id,
        class_id=attendance_session.class_id
    ).first()
    if not enrollment:
        return jsonify({"error": "Student not enrolled in this class"}), 403

    # 5️⃣ Verify attendance code
    if attendance_session.attendance_code != attendance_code:
        return jsonify({"error": "Invalid attendance code"}), 400

    # 6️⃣ Verify location (if coordinates provided)
    if submitted_lat is not None and submitted_lon is not None:
        class_obj = Class.query.get(attendance_session.class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404
        distance = distance_meters(
            float(submitted_lat),
            float(submitted_lon),
            float(class_obj.latitude),
            float(class_obj.longitude)
        )
        if distance > float(class_obj.radius_meters):
            return jsonify({"error": "You are outside the allowed radius"}), 400

    # 7️⃣ Generate device hash
    device_hash = generate_device_hash(
        user_agent or "",
        screen_size or "",
        timezone or "",
        language or "",
        ip_subnet or ""
    )

    # 8️⃣ Check if student already submitted attendance for this session
    existing_record = AttendanceRecord.query.filter_by(
        student_id=user_id,
        session_id=session_id
    ).first()
    if existing_record:
        return jsonify({"error": "Attendance already submitted"}), 400

    # 9️⃣ Create attendance record
    attendance_record = AttendanceRecord(
        #session_id=session_id,
        #student_id=user_id,
        #device_hash=device_hash,
        #submitted_latitude=submitted_lat,
        #submitted_longitude=submitted_lon
        student_id=user_id,
        session_id=session_id,
        device_signature=device_hash,   # ✅ use this name
        ip_prefix=ip_subnet   
    )
    db.session.add(attendance_record)
    db.session.commit()

    return jsonify({"message": "Attendance recorded successfully"}), 201


@attendance_bp.route('/start', methods=['POST'])
def start_attendance():
    # 1️⃣ Verify user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session['user_id']
    user_role = session.get('role')

    # 2️⃣ Verify user is a teacher
    if user_role != 'teacher':
        return jsonify({"error": "Only teachers can start attendance"}), 403

    # 3️⃣ Get JSON data
    data = request.get_json()
    class_id = data.get('class_id')
    attendance_code = data.get('attendance_code')
    starts_at = data.get('starts_at')
    ends_at = data.get('ends_at')
    # latitude = data.get('latitude')
    # longitude = data.get('longitude')
    # radius_meters = data.get('radius_meters')

    # 4️⃣ Check if class exists
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({"error": "Class not found"}), 404
    
    starts_at_dt = parse_iso(starts_at)
    ends_at_dt = parse_iso(ends_at)
    
    # 5️⃣ Create the attendance session
    attendance_session = AttendanceSession(
        class_id=class_id,
        created_by=user_id,
        starts_at=starts_at_dt,
        ends_at=ends_at_dt,
        attendance_code=attendance_code,
        #latitude=latitude,
        #longitude=longitude,
        #radius_meters=radius_meters,
        is_active=True
    )

    db.session.add(attendance_session)
    db.session.commit()

    return jsonify({
        "message": "Attendance session started",
        "attendance_session_id": attendance_session.id
    }), 201

def parse_iso(dt_str):
    # handles "2026-01-31T00:00:00"
    return datetime.fromisoformat(dt_str)


@attendance_bp.route("/active", methods=["GET"])
def get_active_session():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    role = session.get("role")

    class_id = request.args.get("class_id", type=int)
    if not class_id:
        return jsonify({"error": "class_id is required"}), 400

    # If student: must be enrolled
    if role == "student":
        enrollment = Enrollment.query.filter_by(student_id=user_id, class_id=class_id).first()
        if not enrollment:
            return jsonify({"error": "Student not enrolled in this class"}), 403

    # If teacher: must own the class
    if role == "teacher":
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404
        if class_obj.teacher_id != user_id:
            return jsonify({"error": "Not allowed"}), 403

    # Find active session
    now = datetime.now()
    active = AttendanceSession.query.filter_by(class_id=class_id, is_active=True).order_by(AttendanceSession.created_at.desc()).first()

    if not active:
        return jsonify({"active": None}), 200

    # Optional strict window filtering (uncomment if you want)
    # if now < active.starts_at or now > active.ends_at:
    #     return jsonify({"active": None}), 200

    return jsonify({
        "active": {
            "attendance_session_id": active.id,
            "class_id": active.class_id,
            "starts_at": active.starts_at.isoformat() if active.starts_at else None,
            "ends_at": active.ends_at.isoformat() if active.ends_at else None,
            "is_active": bool(active.is_active)
        }
    }), 200


@attendance_bp.route("/end", methods=["POST"])
def end_attendance():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    if session.get("role") != "teacher":
        return jsonify({"error": "Only teachers can end attendance"}), 403

    user_id = session["user_id"]
    data = request.get_json() or {}

    attendance_session_id = data.get("attendance_session_id")
    if not attendance_session_id:
        return jsonify({"error": "attendance_session_id is required"}), 400

    s = AttendanceSession.query.get(attendance_session_id)
    if not s:
        return jsonify({"error": "Attendance session not found"}), 404

    # only creator teacher can end it
    if s.created_by != user_id:
        return jsonify({"error": "Not allowed"}), 403

    s.is_active = False
    db.session.commit()

    return jsonify({"message": "Attendance session ended"}), 200


@attendance_bp.route("/session/<int:attendance_session_id>/records", methods=["GET"])
def get_attendance_records(attendance_session_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    if session.get("role") != "teacher":
        return jsonify({"error": "Only teachers can view attendance records"}), 403

    user_id = session["user_id"]

    s = AttendanceSession.query.get(attendance_session_id)
    if not s:
        return jsonify({"error": "Attendance session not found"}), 404

    if s.created_by != user_id:
        return jsonify({"error": "Not allowed"}), 403

    records = AttendanceRecord.query.filter_by(session_id=attendance_session_id).order_by(AttendanceRecord.marked_at.asc()).all()

    return jsonify({
        "attendance_session_id": attendance_session_id,
        "count": len(records),
        "records": [
            {
                "id": r.id,
                "student_id": r.student_id,
                "status": r.status,
                "device_signature": r.device_signature,
                "ip_prefix": r.ip_prefix,
                "marked_at": r.marked_at.isoformat() if r.marked_at else None
            }
            for r in records
        ]
    }), 200
