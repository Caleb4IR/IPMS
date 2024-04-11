import uuid
from extensions import db
from sqlalchemy.orm import relationship


class Policyholder(db.Model):
    __tablename__ = "policyholders"
    policy_number = db.Column(
        db.String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id = db.Column(db.String(50), db.ForeignKey("users.user_id"))
    user = relationship("User", back_populates="policyholder")

    address = db.Column(db.String(300))
    id_number = db.Column(db.String(50), unique=True, nullable=False)

    policy_id = db.Column(db.String(50), db.ForeignKey("policies.policy_id"))
    policy = relationship("Policy", back_populates="policyholder")

    claims = relationship("Claim", backref="policyholder_ref")

    def to_dict(self):
        return {
            "policy_number": self.policy_number,
            "user_id": self.user_id,
            "address": self.address,
            "id_number": self.id_number,
            "policy_id": self.policy_id,
        }
