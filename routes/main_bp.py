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


from models.policy import Policy

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
def home():
    policies = Policy.query.all()
    return render_template("home.html", policies=policies)
