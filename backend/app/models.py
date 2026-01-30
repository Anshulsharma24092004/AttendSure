from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Basic info
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Role: student or teacher
    role = db.Column(db.Enum('student', 'teacher', name='user_roles'), nullable=False)

    # Account status
    is_active = db.Column(db.Boolean, default=True)

    # Audit info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # Classes taught by this user (only applicable if role='teacher')
    classes_taught = db.relationship('Class', backref='teacher', lazy=True)

    # Enrollments for this user (only applicable if role='student')
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)

    # Attendance records submitted by this user (student)
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)

    def __repr__(self):
        return f"<User {self.id} | {self.name} | {self.role}>"


class Class(db.Model):
    __tablename__ = 'classes'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Basic info
    name = db.Column(db.String(100), nullable=False)

    # Teacher who owns this class
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Location info
    latitude = db.Column(db.Numeric(9,6), nullable=False)
    longitude = db.Column(db.Numeric(9,6), nullable=False)
    radius_meters = db.Column(db.Integer, default=10, nullable=False)  # default radius can be 10 meters

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Audit info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='class', lazy=True)
    attendance_sessions = db.relationship('AttendanceSession', backref='class', lazy=True)

    def __repr__(self):
        return f"<Class {self.id} | {self.name} | Teacher ID {self.teacher_id}>"
    

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Audit info
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_id', name='uq_student_class'),
    )

    def __repr__(self):
        return f"<Enrollment {self.id} | Student {self.student_id} | Class {self.class_id}>"


class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key: the class this session belongs to
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    # Teacher who created the session
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Time window
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    # Verification
    attendance_code = db.Column(db.String(20), nullable=False)  # rotating code
    latitude = db.Column(db.Numeric(9,6), nullable=True)
    longitude = db.Column(db.Numeric(9,6), nullable=True)
    radius_meters = db.Column(db.Integer, nullable=True)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='attendance_session', lazy=True)

    def __repr__(self):
        return f"<AttendanceSession {self.id} | Class {self.class_id} | Created by {self.created_by}>"


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Status
    status = db.Column(db.Enum('present', 'rejected', 'flagged', name='attendance_status'), nullable=False, default='rejected')

    # Evidence
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_latitude = db.Column(db.Numeric(9,6), nullable=True)
    submitted_longitude = db.Column(db.Numeric(9,6), nullable=True)
    distance_from_center = db.Column(db.Numeric(10,2), nullable=True)
    code_matched = db.Column(db.Boolean, nullable=True)
    device_signature_hash = db.Column(db.String(255), nullable=True)
    ip_subnet = db.Column(db.String(50), nullable=True)

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('attendance_session_id', 'student_id', name='uq_session_student'),
    )

    def __repr__(self):
        return f"<AttendanceRecord {self.id} | Session {self.attendance_session_id} | Student {self.student_id} | Status {self.status}>"
