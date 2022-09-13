"""
Time tracker application

This module exposes the WSGI runner as a module-level variable named
``application``

"""

from flask import Flask

application = Flask(__name__)


# authentication routes
@application.route("/signup/")
def signup():
    """New user registration route"""

    return "<h1>New user registration</h1>"


@application.route("/signin/")
def signin():
    """User login route"""

    return "<h1>User login</h1>"


@application.route("/logout/")
def logout():
    """User logout route"""

    return "<h1>User logout</h1>"


# time logs routes
@application.route("/")
def log_list():
    """Time log list route"""

    return "<h1>Time logs list</h1>"


@application.route("/create/")
def log_create():
    """Create a new time log entry"""

    return "<h1>Create new time log</h1>"


@application.route("/update/<int:pk>/")
def log_update(pk: int):
    """Update existing time log entry"""

    return f"<h1>Update time log ID: {pk}</h1>"


@application.route("/delete/<int:pk>/")
def log_delete(pk: int):
    """Delete existing time log entry"""

    return f"<h1>Delete time log ID: {pk}</h1>"


if __name__ == "__main__":
    application.run()
