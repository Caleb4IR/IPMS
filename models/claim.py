import uuid
from extensions import db
from sqlalchemy.orm import relationship
from datetime import date


class Claim(db.Model):
    __tablename__ = "claims"
    claim_id = db.Column(
        db.String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    policy_number = db.Column(
        db.String(50), db.ForeignKey("policyholders.policy_number"), nullable=False
    )
    policyholder = relationship(
        "Policyholder",
        backref="related_claims",
        overlaps="policyholder_ref, claims",
    )

    name = db.Column(db.String(100), nullable=False)

    claim_description = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending Approval")

    def to_dict(self):
        return {
            "claim_id": self.claim_id,
            "name": self.name,
            "claim_description": self.claim_description,
            "submission_date": self.submission_date,
            "status": self.status,
        }
