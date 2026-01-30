from app.extensions import db


class Class(db.Model):
    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    radius_meters = db.Column(db.Integer, nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
