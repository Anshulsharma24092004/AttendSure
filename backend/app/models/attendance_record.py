from app.extensions import db


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("attendance_sessions.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="present"
    )

    device_signature = db.Column(db.String(255), nullable=True)

    ip_prefix = db.Column(db.String(50), nullable=True)

    marked_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
