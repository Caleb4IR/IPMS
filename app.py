import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from dotenv import load_dotenv
from pprint import pprint
import uuid
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
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
    role_id = db.Column(db.String(50), nullable=False, default="3")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role_id": self.role_id,
        }


class Policy(db.Model):
    __tablename__ = "policies"
    policy_id = db.Column(db.String(50), primary_key=True)
    coverage = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200))
    premium = db.Column(db.Float)

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
    user_id = db.Column(db.String(50))
    address = db.Column(db.String(300))
    id_number = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {
            "policy_number": self.policy_number,
            "user_id": self.user_id,
            "address": self.address,
            "id_number": self.id_number,
        }


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


@app.route("/dashboard")
def customer_dashboard():
    return render_template("customer_dashboard.html")


# USERS CRUD OPERATIONS
# GET users
@app.get("/users")
def get_users():
    return jsonify(users)


# GET user by id
@app.get("/users/<id>")
def get_users_by_id(id):
    filtered_user = next((user for user in users if user["id"] == id), None)
    if filtered_user:
        return jsonify(filtered_user)
    else:
        return jsonify({"message": "User not found"}), 404


# DELETE user by id
@app.delete("/users/<id>")
def delete_user(id):
    deleted_user = next((user for user in users if user["id"] == id), None)
    if deleted_user:
        users.remove(deleted_user)
        return jsonify({"message": "Movie deleted sucessfully", "data": deleted_user})
    else:
        return jsonify({"message": "Movie not found"}), 404


# Update a user
@app.put("/users/<id>")
def update_user_by_id(id):
    data = request.json

    user_to_update = next((user for user in users if user["id"] == id), None)
    if user_to_update:
        user_to_update.update(data)
        return jsonify({"message": "Movie updated", "data": user_to_update})
    else:
        return jsonify({"message": "Movie not updated"}), 404


# POLICY CRUD OPERATIONS
