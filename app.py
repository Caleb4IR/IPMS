import datetime
import os
from flask import Flask, jsonify, redirect, request, render_template, url_for, flash
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


app = Flask(__name__)


load_dotenv()
pprint(os.environ.get("AZURE_DATABASE_URL"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FORM_SECRET_KEY")

connection_string = os.environ.get("AZURE_DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = connection_string

db.init_app(app)

from routes.user_bp import user_bp

app.register_blueprint(user_bp, url_prefix="/user")

from routes.policyholder_bp import policyholder_bp

app.register_blueprint(policyholder_bp)

from routes.policy_bp import policy_bp

app.register_blueprint(policy_bp)

from routes.main_bp import main_bp

app.register_blueprint(main_bp)

from routes.claim_bp import claim_bp

app.register_blueprint(claim_bp)

try:
    with app.app_context():
        # Use text() to explicitly declare your SQL command
        result = db.session.execute(text("SELECT 1")).fetchall()
        print("Connection successful:", result)
        db.create_all()

except Exception as e:
    print("Error connecting to the database:", e)
