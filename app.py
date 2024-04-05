import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from dotenv import load_dotenv
from pprint import pprint
import uuid
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError

app = Flask(__name__)

policyholder = [
    {
        "policyholder_id": "1",
        "user_id": "1",
        "policy_id": "3",
        "start_date": "2024-03-17",
        "id_number": 1234567891012,
        "address": "124 school str Claremont",
    },
    {
        "policyholder_id": "4",
        "user_id": "4",
        "policy_id": "1",
        "start_date": "2024-03-17",
        "id_number": 1234567891015,
        "address": "85 Marlin Close Fish Hoek",
    },
]


load_dotenv()
pprint(os.environ.get("AZURE_DATABASE_URL"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FORM_SECRET_KEY")

connection_string = os.environ.get("AZURE_DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = connection_string

db = SQLAlchemy(app)


try:
    with app.app_context():
        # Use text() to explicitly declare your SQL command
        result = db.session.execute(text("SELECT 1")).fetchall()
        print("Connection successful:", result)

except Exception as e:
    print("Error connecting to the database:", e)


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(
        db.String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role_id = db.Column(
        db.String(50), db.ForeignKey("roles.role_id"), nullable=False, default="3"
    )
    role = relationship("Role", back_populates="users")
    policyholder = relationship("Policyholder", back_populates="users")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role_id,
        }


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


class Role(db.Model):
    __tablename__ = "roles"
    role_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50))
    users = relationship("User", back_populates="role")

    def to_dict(self):
        return {
            "role_id": self.role_id,
            "name": self.name,
        }


class Policyholder(db.Model):
    __tablename__ = "policyholders"
    policy_number = db.Column(
        db.String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id = db.Column(db.String(50), db.ForeignKey("users.user_id"))
    users = relationship("User", back_populates="policyholder")

    address = db.Column(db.String(300))
    id_number = db.Column(db.String(50), unique=True, nullable=False)

    policy_id = db.Column(db.String(50), db.ForeignKey("policies.policy_id"))
    policy = relationship("Policy", back_populates="policyholder")

    def to_dict(self):
        return {
            "policy_number": self.policy_number,
            "user_id": self.user_id,
            "address": self.address,
            "id_number": self.id_number,
            "policy_id": self.policy_id,
        }


# class Claim(db.Model):
#     __tablename__ = "claims"
#     claim_id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
#     policy_id = db.Column(db.String(50))
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), nullable=False)
#     policy_number = db.Column(db.String(50), nullable=False)
#     claim_description = db.Column(db.Text, nullable=False)


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


@app.route("/user/register", methods=["GET", "POST"])
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
            return "<h1>Registration Successful</h1>"
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


@app.route("/user/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        return "<h1>Login successful</h1>"

    return render_template("login.html", form=form)


# class RegistrationFormAdmin(FlaskForm):
#     name = StringField("Name", validators=[InputRequired(), Length(min=6)])
#     email = StringField("Email", validators=[InputRequired(), Length(min=11)])
#     password = PasswordField(
#         "Password", validators=[InputRequired(), Length(min=8, max=12)]
#     )
#     role = SelectField("Role", choices=[("1", "Admin"), ("2", "Agent")])
#     submit = SubmitField("Register")

#     # def validate_<fieldname>
#     def validate_email(self, field):  # Automatically called when submit happens
#         # inform WTF that there is an error
#         print("Validate email", field.data)
#         if User.query.filter_by(email=field.data).first():
#             raise ValidationError("Email taken")


# @app.route("/user/register", methods=["GET", "POST"])
# def register_page():
#     form = RegistrationFormAdmin()

#     name = request.form.get("name")
#     email = request.form.get("email")
#     password = request.form.get("password")

#     # Only works with POST
#     if form.validate_on_submit():
#         new_user = User(name=name, email=email, password=password)
#         try:
#             db.session.add(new_user)
#             db.session.commit()
#             return "<h1>Registration Successful</h1>"
#         except Exception as e:
#             db.session.rollback()
#             return "<h1>Server Error</h1>", 500

#     # GET issues token
#     return render_template("admin_agent_register.html", form=form)


@app.route("/admin/dashboard")
def admin_dashboard():
    total_users = User.query.count()
    total_policies = Policy.query.count()
    return render_template(
        "admin_dashboard.html", total_users=total_users, total_policies=total_policies
    )


@app.route("/")
def home():
    policies = Policy.query.all()
    return render_template("home.html", policies=policies)


@app.route("/profile")
def profile():
    return render_template("profile.html", users=users)


@app.route("/cover/<policy_id>")
def comprehensive(policy_id):
    policy = Policy.query.filter_by(policy_id="1").first()
    if policy:
        return render_template("third_party.html", policy=policy.to_dict())
    else:
        return "Policy not found", 404


@app.route("/cover/3")
def third_party():
    policy = Policy.query.filter_by(policy_id="3").first()
    if policy:
        return render_template("third_party.html", policy=policy.to_dict())
    else:
        return "Policy not found", 404


@app.route("/cover/2")
def fire_theft():
    policy = Policy.query.filter_by(policy_id="2").first()
    if policy:
        return render_template("fire_theft.html", policy=policy.to_dict())
    else:
        return "Policy not found", 404


@app.route("/admin/user-list")
def user_list_page():
    users = User.query.all()
    return render_template("user-list.html", users=users)


# DELETE user by id
@app.route("/user-list/delete", methods=["POST"])  # HOF
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
@app.route("/user-list/<user_id>/update", methods=["GET"])
def update_user_form(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template("update_user.html", user=user)
    else:
        return "User not found", 404


@app.route("/user-list/update", methods=["POST"])
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


# POLICY CRUD OPERATIONS


@app.route("/admin/policy-list")
def policy_list_page():
    policies = Policy.query.all()
    return render_template("policy-list.html", policies=policies)


# DELETE policy by id
@app.route("/policy-list/delete", methods=["POST"])  # HOF
def delete_policy_by_id():
    id = request.form.get("policy_id")
    filtered_policy = Policy.query.get(id)
    if not filtered_policy:
        return "<h1>Policy not found</h1>", 404

    try:
        db.session.delete(filtered_policy)
        db.session.commit()  # Making the change (update/delete/create) permanent
        return f"<h1>Policy deleted Successfully</h1>"
    except Exception as e:
        db.session.rollback()  # Undo the change
        return f"<h1>Error happened {str(e)}</h1>", 500


# Update a policy
@app.route("/policy-list/<policy_id>/update", methods=["GET"])
def update_polcy_form(policy_id):
    policy = Policy.query.get(policy_id)
    if policy:
        return render_template("update_policy.html", policy=policy)
    else:
        return "Policy not found", 404


@app.route("/policy-list/update", methods=["POST"])
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
        return "<h1>Premium updated</h1>"
    except Exception as e:
        db.session.rollback()
        return "<h1>Server Error</h1>", 500


# Claim Submission
class ClaimsForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[InputRequired(), Length(min=6, max=100)])
    policy_number = StringField(
        "Policy Number", validators=[InputRequired(), Length(min=6, max=50)]
    )
    claim_description = TextAreaField(
        "Claim Description", validators=[InputRequired(), Length(min=10, max=1000)]
    )
    submit = SubmitField("Submit")


@app.route("/submit_claim", methods=["GET", "POST"])
def submit_claim():
    form = ClaimsForm()
    if form.validate_on_submit():
        # Create a new claim instance
        new_claim = Claim(
            name=form.name.data,
            email=form.email.data,
            policy_number=form.policy_number.data,
            claim_description=form.claim_description.data,
        )

        # Add the claim to the database session
        db.session.add(new_claim)

        # Commit the changes to the database
        db.session.commit()

        return "<h1>Claim submitted</h1>"

    return render_template("claim_submission_form.html", form=form)
