from flask import Flask, Blueprint, redirect, request, render_template, url_for, flash
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import not_
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
from models.policy import Policy
from models.policyholder import Policyholder
from models.user import User

policyholder_bp = Blueprint("policyholder_bp", __name__)


@policyholder_bp.route("/agent/dashboard")
@login_required
def agent_dashboard():
    total_users = Policyholder.query.count()
    total_claims = Claim.query.filter_by(status="Pending Approval").count()
    return render_template(
        "agent_dashboard.html", total_users=total_users, total_claims=total_claims
    )


# CRUD operations for policyholder
class AddPolicyholderForm(FlaskForm):
    user = SelectField("Select User", coerce=str)
    policy = SelectField("Select Policy", coerce=str)
    address = TextAreaField("Address", validators=[InputRequired()])
    id_number = StringField("ID Number", validators=[InputRequired()])


@policyholder_bp.route("/agent/add-policyholder", methods=["GET", "POST"])
def add_policyholder():
    form = AddPolicyholderForm()

    form.user.choices = [
        (user.user_id, user.name)
        for user in User.query.filter(
            not_(User.user_id.in_(db.session.query(Policyholder.user_id).distinct()))
        )
        .filter_by(role_id="3")
        .all()
    ]

    # Populate policy choices from the policy table
    form.policy.choices = [
        (policy.policy_id, policy.coverage) for policy in Policy.query.all()
    ]

    if form.validate_on_submit():
        user_id = form.user.data
        policy_id = form.policy.data
        address = request.form.get("address")
        id_number = request.form.get("id_number")

        # Create a new Policyholder object
        new_policyholder = Policyholder(
            user_id=user_id, address=address, id_number=id_number, policy_id=policy_id
        )

        # Add the new policyholder to the database session
        db.session.add(new_policyholder)
        db.session.commit()

        flash("Policyholder added successfully!", "success")
        return redirect(url_for("policyholder_bp.add_policyholder"))

    return render_template("add_policyholder.html", form=form)


@policyholder_bp.route("/agent/policyholder-list")
def user_list_page():
    users = Policyholder.query.all()
    return render_template("policyholder-list.html", users=users)


@policyholder_bp.route("/agent/user-list/delete", methods=["POST"])  # HOF
def delete_policyholder_by_id():
    policy_number = request.form.get("policy_number")

    policyholder = Policyholder.query.filter_by(policy_number=policy_number).first()
    if not policyholder:
        return "<h1>Policyholder not found</h1>", 404

    try:
        db.session.delete(policyholder)
        db.session.commit()
        flash("Policyholder deleted!", "success")
        return redirect(url_for("policyholder_bp.user_list_page"))
    except Exception as e:
        db.session.rollback()
        return f"<h1>Error occurred: {str(e)}</h1>", 500
