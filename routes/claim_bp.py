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
class ClaimForm(FlaskForm):
    policy_number = StringField("Policy Number", validators=[InputRequired()])
    name = StringField("Customer Name", validators=[InputRequired()])
    claim_description = TextAreaField("Claim Description", validators=[InputRequired()])
    submit = SubmitField("Submit")


# Route to handle claim submission
@claim_bp.route("/claims", methods=["GET", "POST"])
def claim_form():
    form = ClaimForm()
    if form.validate_on_submit():
        policy_number = form.policy_number.data
        name = form.name.data
        claim_description = form.claim_description.data

        # Check if policy number exists in policyholder table
        policyholder = Policyholder.query.filter_by(policy_number=policy_number).first()
        if policyholder is None:
            return "<h1>Policy number does not exist.<h1>"

        # Create a new claim
        new_claim = Claim(
            policy_number=policy_number, name=name, claim_description=claim_description
        )
        db.session.add(new_claim)
        db.session.commit()

        flash("Claim submitted successfully.", "success")
        return redirect(url_for("claim_bp.claim_form"))

    return render_template("claim_form.html", form=form)


@claim_bp.route("/agent/claim-list")
def claim_list():
    pending_claims = Claim.query.filter_by(status="Pending Approval").all()
    return render_template("claims-list.html", claims=pending_claims)


@claim_bp.route("/update_claim_status", methods=["POST"])
def update_claim_status():
    claim_id = request.form["claim_id"]
    new_status = request.form["status"]

    claim = Claim.query.get(claim_id)
    if claim:
        claim.status = new_status
        db.session.commit()
        flash("Claim status updated successfully.", "success")
    else:
        flash("Claim not found.", "error")

    return redirect(url_for("claim_bp.claim_list"))
