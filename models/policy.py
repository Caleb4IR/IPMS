import uuid
from extensions import db
from sqlalchemy.orm import relationship


class Policy(db.Model):
    __tablename__ = "policies"
    policy_id = db.Column(db.String(50), primary_key=True)
    coverage = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200))
    premium = db.Column(db.Float)
    policyholder = relationship("Policyholder", back_populates="policy")

    def to_dict(self):
        return {
            "policy_id": self.policy_id,
            "coverage": self.coverage,
            "image": self.image,
            "premium": self.premium,
        }
