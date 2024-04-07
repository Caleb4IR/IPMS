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
from models.role import Role
from models.user import User
from models.policy import Policy

user_bp = Blueprint("user_bp", __name__)


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=6)])
    email = StringField("Email", validators=[InputRequired(), Length(min=11)])
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=12)]
    )
    submit = SubmitField("Register")

    # def validate_<fieldname>
    def validate_email(self, field):  # Automatically called when submit happens
        # inform WTF that there is an error
        print("Validate email", field.data)
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email taken")


@user_bp.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegistrationForm()

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    # Only works with POST
    if form.validate_on_submit():
        new_user = User(name=name, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login_page"))
        except Exception as e:
            db.session.rollback()
            return "<h1>Server Error</h1>", 500

    # GET issues token
    return render_template("register.html", form=form)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Length(min=11)])
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=12)]
    )
    submit = SubmitField("Login")

    def validate_email(self, field):  # Automatically called when submit happens
        # inform WTF that there is an error
        print("Validate email", field.data)
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError("Invaild Credentials")

    def validate_password(self, field):  # Automatically called when submit happens
        user_from_db = User.query.filter_by(email=self.email.data).first()

        if user_from_db:
            user_db_data = user_from_db.to_dict()
            form_password = field.data
            print(user_db_data, form_password)

            if user_db_data["password"] != form_password:
                raise ValidationError("Invaild Credentials")


@user_bp.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        return redirect(url_for("home"))

    return render_template("login.html", form=form)


class RegistrationFormAdmin(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=6)])
    email = StringField("Email", validators=[InputRequired(), Length(min=11)])
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=12)]
    )
    role = SelectField("Role", choices=[("1", "Admin"), ("2", "Agent")])
    submit = SubmitField("Register")

    # def validate_<fieldname>
    def validate_email(self, field):  # Automatically called when submit happens
        # inform WTF that there is an error
        print("Validate email", field.data)
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email taken")


@user_bp.route("/admin/register", methods=["GET", "POST"])
def admin_register_page():
    form = RegistrationFormAdmin()

    name = request.form.get("name")
    email = request.form.get("email")
    role_id = request.form.get("role")
    password = request.form.get("password")

    role = Role.query.filter_by(role_id=role_id).first()

    # Only works with POST
    if form.validate_on_submit():
        new_user = User(name=name, email=email, password=password, role=role)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login_page"))
        except Exception as e:
            db.session.rollback()
            return "<h1>Server Error</h1>", 500

    # GET issues token
    return render_template("admin_agent_register.html", form=form)


@user_bp.route("/admin/user-list")
def user_list_page():
    users = User.query.all()
    return render_template("user-list.html", users=users)


# DELETE user by id
@user_bp.route("/admin/user-list/delete", methods=["POST"])  # HOF
def delete_user_by_id():
    id = request.form.get("user_id")
    filtered_user = User.query.get(id)
    if not filtered_user:
        return "<h1>User not found</h1>", 404

    try:
        db.session.delete(filtered_user)
        db.session.commit()  # Making the change (update/delete/create) permanent
        return f"<h1>User deleted Successfully</h1>"
    except Exception as e:
        db.session.rollback()  # Undo the change
        return f"<h1>Error happened {str(e)}</h1>", 500


# Update a user
@user_bp.route("/admin/user-list/<user_id>/update", methods=["GET"])
def update_user_form(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template("update_user.html", user=user)
    else:
        return "User not found", 404


@user_bp.route("/admin/user-list/update", methods=["POST"])
def update_user():
    user_id = request.form.get("user_id")
    user_to_update = User.query.get(user_id)

    if not user_to_update:
        return "<h1>User not found</h1>", 404

    try:
        user_to_update.name = request.form.get("name")
        user_to_update.email = request.form.get("email")

        db.session.commit()
        return "<h1>User updated</h1>"
    except Exception as e:
        db.session.rollback()
        return "<h1>Server Error</h1>", 500


@user_bp.route("/admin/dashboard")
def admin_dashboard():
    total_users = User.query.count()
    total_policies = Policy.query.count()
    return render_template(
        "admin_dashboard.html", total_users=total_users, total_policies=total_policies
    )
