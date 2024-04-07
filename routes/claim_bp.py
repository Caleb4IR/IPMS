import datetime
from flask import Flask, Blueprint, redirect, request, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from dotenv import load_dotenv
from pprint import pprint
import uuid
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError

from extensions import db
from models.claim import Claim
from models.policyholder import Policyholder

claim_bp = Blueprint("claim_bp", __name__)


# Claim Submission
class ClaimsForm(FlaskForm):
    policy_number = StringField("Policy Number", validators=[InputRequired()])
    name = StringField("Name", validators=[InputRequired()])
    claim_description = TextAreaField("Description", validators=[InputRequired()])
    submit = SubmitField("Submit")


# Route to handle claim submission
@claim_bp.route("/claims", methods=["GET", "POST"])
def claims():
    form = ClaimsForm()

    if form.validate_on_submit():
        policy_number = request.form.get("policy_number")
        name = request.form.get("name")
        claim_description = request.form.get("claim_description")

        # Get policyholder based on policy number
        policyholder = Policyholder.query.filter_by(policy_number=policy_number).first()

        if policyholder:
            # Create a new Claim object
            new_claim = Claim(
                policy_id=policyholder.policy_id,
                policy_number=policy_number,
                name=name,
                claim_description=claim_description,
                submission_date=datetime.now(),
                status="Pending Approval",
            )

            # Add the new claim to the database session
            db.session.add(new_claim)
            db.session.commit()
            flash("Claim submitted successfully!", "success")
            return redirect(url_for("claims"))

        else:
            flash("Error: Policy number not found.", "error")

    return render_template("claim_form.html", form=form)
