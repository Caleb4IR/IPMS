import uuid
from extensions import db
from sqlalchemy.orm import relationship


class Claim(db.Model):
    __tablename__ = "claims"
    claim_id = db.Column(
        db.String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    policy_id = db.Column(
        db.String(50), db.ForeignKey("policies.policy_id"), nullable=False
    )
    policy = relationship("Policy", backref="claims")

    policy_number = db.Column(
        db.String(50), db.ForeignKey("policyholders.policy_number"), nullable=False
    )
    policyholder = relationship(
        "Policyholder", backref="related_claims", overlaps="policyholder_ref"
    )

    name = db.Column(db.String(100), nullable=False)

    claim_description = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending Approval")

    def to_dict(self):
        return {
            "claim_id": self.claim_id,
            "policy_id": self.policy_id,
            "name": self.name,
            "claim_description": self.claim_description,
            "submission_date": self.submission_date,
            "status": self.status,
        }
