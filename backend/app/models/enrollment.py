from app.extensions import db


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    class_id = db.Column(
        db.Integer,
        db.ForeignKey("classes.id"),
        nullable=False
    )

    is_active = db.Column(db.Boolean, default=True)

    enrolled_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
