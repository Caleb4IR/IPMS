import uuid
from extensions import db
from sqlalchemy.orm import relationship
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "users"
    user_id = db.Column(
        db.String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role_id = db.Column(
        db.String(50), db.ForeignKey("roles.role_id"), nullable=False, default="3"
    )
    role = relationship("Role", back_populates="users")
    policyholder = relationship("Policyholder", back_populates="user")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role_id,
        }

    def get_id(self):
        return self.user_id
