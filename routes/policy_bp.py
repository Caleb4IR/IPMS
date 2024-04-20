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

policy_bp = Blueprint("policy_bp", __name__)


@policy_bp.route("/cover/1")
def comprehensive():
    policy = Policy.query.filter_by(policy_id="1").first()
    if policy:
        return render_template("comprehensive.html", policy=policy.to_dict())
    else:
        return "Policy not found", 404


@policy_bp.route("/cover/3")
def third_party():
    policy = Policy.query.filter_by(policy_id="3").first()
    if policy:
        return render_template("third_party.html", policy=policy.to_dict())
    else:
        return "Policy not found", 404


@policy_bp.route("/cover/2")
def fire_theft():
    policy = Policy.query.filter_by(policy_id="2").first()
    if policy:
        return render_template("fire_theft.html", policy=policy.to_dict())
    else:
        return "Policy not found", 404


# POLICY CRUD OPERATIONS


@policy_bp.route("/user/admin/policy-list")
def policy_list_page():
    policies = Policy.query.all()
    return render_template("policy-list.html", policies=policies)


# DELETE policy by id
@policy_bp.route("/admin/policy-list/delete", methods=["POST"])  # HOF
def delete_policy_by_id():
    id = request.form.get("policy_id")
    filtered_policy = Policy.query.get(id)
    if not filtered_policy:
        return "<h1>Policy not found</h1>", 404

    try:
        db.session.delete(filtered_policy)
        db.session.commit()  # Making the change (update/delete/create) permanent
        flash("Policy deleted", "success")
        return redirect(url_for("policy_bp.policy_list_page"))
    except Exception as e:
        db.session.rollback()  # Undo the change
        return f"<h1>Error happened {str(e)}</h1>", 500


# Update a policy
@policy_bp.route("/user/admin/policy-list/<policy_id>/update", methods=["GET"])
def update_polcy_form(policy_id):
    policy = Policy.query.get(policy_id)
    if policy:
        return render_template("update_policy.html", policy=policy)
    else:
        return "Policy not found", 404


@policy_bp.route("/user/admin/policy-list/update", methods=["POST"])
def update_policy():
    policy_id = request.form.get("policy_id")
    policy_to_update = Policy.query.get(policy_id)

    if not policy_to_update:
        return "<h1>Policy not found</h1>", 404

    try:
        policy_to_update.coverage = request.form.get("coverage")
        policy_to_update.image = request.form.get("image")
        policy_to_update.premium = request.form.get("premium")

        db.session.commit()
        flash("Policy updated", "success")
        return redirect(url_for("policy_bp.policy_list_page"))
    except Exception as e:
        db.session.rollback()
        return "<h1>Server Error</h1>", 500
