import uuid
from extensions import db
from sqlalchemy.orm import relationship


class Role(db.Model):
    __tablename__ = "roles"
    role_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50))
    users = relationship("User", back_populates="role")

    def to_dict(self):
        return {
            "role_id": self.role_id,
            "name": self.name,
        }
