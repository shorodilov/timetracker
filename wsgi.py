"""
Time tracker application

This module exposes the WSGI runner as a module-level variable named
``application``

"""
import datetime

from flask import abort, Flask, redirect, render_template, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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


# authentication forms
# TODO: add auth forms

# authentication routes
@application.route("/signup/")
def signup():
    """New user registration route"""

    return render_template("signup.html")


@application.route("/signin/")
def signin():
    """User login route"""

    return render_template("signin.html")


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
