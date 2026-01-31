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
        starts_at=starts_at,
        ends_at=ends_at,
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