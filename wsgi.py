"""
Time tracker application

This module exposes the WSGI runner as a module-level variable named
``application``

"""

import datetime

from flask import abort, flash, Flask, redirect, render_template, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField, PasswordField,
    StringField,
    SubmitField
)
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from utils import get_log, logs

application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
application.config["SECRET_KEY"] = "flask-secret-key"
db = SQLAlchemy(application)
migrate = Migrate(application, db)


# authentication models
class UserModel(db.Model):
    """User model implementation"""

    __tablename__ = "auth_user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64), default="")
    last_name = db.Column(db.String(64), default="")

    def __repr__(self) -> str:
        """Return a string representation of an instance"""

        return f"<UserModel(username='{self.username}', email='{self.email}')>"

    def __str__(self) -> str:
        """Return a string version of an instance"""

        first_name = self.first_name or ""
        last_name = self.last_name or ""
        fullname = " ".join([first_name, last_name]).rstrip()

        return fullname or self.username

    def check_password(self, password: str) -> bool:
        """Check passed raw password with user assigned"""

        # TODO: add implementation

    @staticmethod
    def generate_hashed_password(raw_password: str) -> str:
        """Return hashed password"""

        # TODO: add implementation
        return raw_password


# authentication forms
class SignUpForm(FlaskForm):
    """New user form"""

    username = StringField("Username", [DataRequired(), Length(max=128)])
    password = PasswordField("Password", [DataRequired(), Length(max=128)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    email = EmailField("Email", [DataRequired()])
    first_name = StringField("First Name", [Length(max=64)])
    last_name = StringField("Last Name", [Length(max=64)])

    submit = SubmitField("Sign Up")

    # noinspection PyMethodMayBeStatic
    def validate_username(self, username: StringField) -> None:
        user = UserModel.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("This username is already registered.")

    # noinspection PyMethodMayBeStatic
    def validate_email(self, email: StringField) -> None:
        user = UserModel.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("This email is already registered.")


class SignInForm(FlaskForm):
    """User login form"""

    username = StringField("Username", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    remember = BooleanField("Remember Me", default=True)

    submit = SubmitField("Sign In")


# authentication routes
@application.route("/signup/", methods=["GET", "POST"])
def signup():
    """New user registration route"""

    form = SignUpForm()
    if form.validate_on_submit():
        db.session.add(
            UserModel(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=UserModel.generate_hashed_password(form.password.data)
            )
        )
        db.session.commit()
        flash("Account created. You can login now.", "success")
        return redirect(url_for("signin"))

    return render_template("signup.html", form=form)


@application.route("/signin/", methods=["GET", "POST"])
def signin():
    """User login route"""

    form = SignInForm()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            ...  # TODO: login user
        else:
            flash("Incorrect username or password. Please check.", "danger")

    return render_template("signin.html", form=form)


@application.route("/logout/")
def logout():
    """User logout route"""

    redirect_to = url_for("log_list")

    return redirect(redirect_to)


# time logs models
def get_current_timestamp() -> datetime.datetime:
    return datetime.datetime.now()


def get_current_date() -> datetime.date:
    return get_current_timestamp().date()


class TimeLogModel(db.Model):
    """Time log model implementation"""

    __tablename__ = "time_log"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column("time_reported", db.Numeric(precision=2), nullable=False)
    date = db.Column(
        "date_reported", db.Date, nullable=False, default=get_current_date
    )
    # TODO: fix normalization
    task_uid = db.Column(db.String(32), nullable=False)
    task_title = db.Column(db.String(128), nullable=False)

    def __repr__(self) -> str:
        """Return a string representation of an instance"""

        return f"<TimeLogModel({self})>"

    def __str__(self) -> str:
        """Return a string version of an instance"""

        reported = {
            "time_reported": self.value,
            "date_reported": self.date
        }

        return f"task_uid={self.task_uid}, {reported}"


# time logs forms
# TODO: add log forms

# time logs routes
@application.route("/")
def log_list():
    """Time log list route"""

    return render_template("log_list.html", object_list=logs)


@application.route("/create/")
def log_create():
    """Create a new time log entry"""

    return render_template("log_form.html")


@application.route("/update/<int:pk>/")
def log_update(pk: int):
    """Update existing time log entry"""

    log = get_log(pk)
    if log:
        return render_template("log_form.html", object=log)

    abort(404)


@application.route("/delete/<int:pk>/")
def log_delete(pk: int):
    """Delete existing time log entry"""

    log = get_log(pk)
    if log:
        return render_template("log_delete.html", object=log)

    abort(404)


if __name__ == "__main__":
    application.run()
