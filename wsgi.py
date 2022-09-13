"""
Time tracker application

This module exposes the WSGI runner as a module-level variable named
``application``

"""

from flask import abort, Flask, redirect, render_template, url_for

from utils import get_log, logs

application = Flask(__name__)


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
