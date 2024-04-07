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
from models.policy import Policy
from models.policyholder import Policyholder
from models.user import User

policyholder_bp = Blueprint("policyholder_bp", __name__)


# CRUD operations for policyholder
class AddPolicyholderForm(FlaskForm):
    user = SelectField("Select User", coerce=str)
    policy = SelectField("Select Policy", coerce=str)
    address = TextAreaField("Address", validators=[InputRequired()])
    id_number = TextAreaField("ID Number", validators=[InputRequired()])


@policyholder_bp.route("/agent/add-policyholder", methods=["GET", "POST"])
def add_policyholder():
    form = AddPolicyholderForm()

    # Populate user choices from the user table where role is 1
    form.user.choices = [
        (user.user_id, user.name) for user in User.query.filter_by(role_id="3").all()
    ]

    # Populate policy choices from the policy table
    form.policy.choices = [
        (policy.policy_id, policy.coverage) for policy in Policy.query.all()
    ]

    if form.validate_on_submit():
        user_id = request.form.get("user_id")
        policy_id = request.form.get("policy_id")
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
        return redirect(url_for("add_policyholder"))

    return render_template("add_policyholder.html", form=form)