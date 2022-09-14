"""
Time tracker application

This module exposes the WSGI runner as a module-level variable named
``application``

"""

import datetime

from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_bcrypt import Bcrypt
from flask_login import (
    current_user,
    login_user,
    LoginManager,
    logout_user,
    UserMixin,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField, DateField, DecimalField, EmailField, PasswordField,
    SelectField, StringField, SubmitField
)
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
application.config["SECRET_KEY"] = "flask-secret-key"
db = SQLAlchemy(application)
migrate = Migrate(application, db)
bcrypt = Bcrypt(application)
login_manager = LoginManager(application)


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))


# authentication models
class UserModel(db.Model, UserMixin):
    """User model implementation"""

    __tablename__ = "auth_user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64), default="")
    last_name = db.Column(db.String(64), default="")
    logs = db.relationship("TimeLogModel", backref="reporter", lazy=True)

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

        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def generate_hashed_password(raw_password: str) -> str:
        """Return hashed password"""

        return bcrypt.generate_password_hash(raw_password)


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
        # noinspection PyArgumentList
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
            login_user(user, remember=form.remember.data)

            return redirect(url_for("log_list"))

        else:
            flash("Incorrect username or password. Please check.", "danger")

    return render_template("signin.html", form=form)


@application.route("/logout/")
def logout():
    """User logout route"""

    logout_user()
    redirect_to = url_for("log_list")

    return redirect(redirect_to)


# time logs models
def get_current_timestamp() -> datetime.datetime:
    return datetime.datetime.now()


def get_current_date() -> datetime.date:
    return get_current_timestamp().date()


class TaskModel(db.Model):
    """Task model implementation"""

    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)  # TODO: change to UUID
    title = db.Column(db.String(128), nullable=False)
    logs = db.relationship("TimeLogModel", backref="task", lazy=True)

    def __repr__(self) -> str:
        """Return a string representation of instance"""

        return f"<TaskModel(title='{self.title}')>"

    def __str__(self) -> str:
        """Return a string version of an instance"""

        return self.title


class TimeLogModel(db.Model):
    """Time log model implementation"""

    __tablename__ = "time_log"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column("time_reported", db.Numeric(precision=2), nullable=False)
    date = db.Column(
        "date_reported", db.Date, nullable=False, default=get_current_date
    )

    task_id = db.Column(
        db.Integer, db.ForeignKey(TaskModel.id), nullable=False
    )
    reporter_id = db.Column(
        db.Integer, db.ForeignKey(UserModel.id), nullable=False
    )

    @property
    def time_reported(self):
        return self.value

    @property
    def date_reported(self):
        return self.date

    def __repr__(self) -> str:
        """Return a string representation of an instance"""

        return f"<TimeLogModel({self})>"

    def __str__(self) -> str:
        """Return a string version of an instance"""

        return (f"task_title={self.task.title}, "
                f"time_reported={self.value}, "
                f"date_reported={self.date}")


# time logs formatters
@application.template_filter("date")
def format_date(value: datetime.date, formatter: str = "%b %d, %y") -> str:
    return value.strftime(formatter)


@application.template_filter("decimal")
def format_decimal(value: float, places: int = 2) -> str:
    return f"{value:.{places}f}"


# time logs forms
class TimeLogForm(FlaskForm):
    """Time log report form implementation"""

    task_choices = [(task.id, task.title) for task in TaskModel.query.all()]

    task = SelectField("Task", [DataRequired()], choices=task_choices)
    time_reported = DecimalField("Time spent", [DataRequired()])
    date_reported = DateField(
        "Date", [DataRequired()], default=get_current_date
    )

    # noinspection PyMethodMayBeStatic
    def validate_task(self, task: SelectField):
        task_id = int(task.data)
        if TaskModel.query.get(task_id) is None:
            raise ValidationError("Could not find task.")

    # noinspection PyMethodMayBeStatic
    def validate_time_reported(self, time_reported: DecimalField):
        if time_reported.data < 0.1:
            raise ValidationError("Minimum value is 0.1")
        if time_reported.data > 24:
            raise ValidationError("Maximum value is 24")

    # noinspection PyMethodMayBeStatic
    def validate_date_reported(self, date_reported: DateField):
        if date_reported.data > get_current_date():
            raise ValidationError("Future reports are restricted.")


# time logs routes
@application.route("/")
def log_list():
    """Time log list route"""

    if current_user.is_authenticated:
        object_list = current_user.logs
    else:
        object_list = []

    return render_template("log_list.html", object_list=object_list)


# TODO: login required
@application.route("/create/", methods=["GET", "POST"])
def log_create():
    """Create a new time log entry"""

    form = TimeLogForm()
    if form.validate_on_submit():
        db.session.add(
            TimeLogModel(
                reporter_id=current_user.id,
                task_id=int(form.task.data),
                value=form.time_reported.data,
                date=form.date_reported.data,
            )
        )
        db.session.commit()
        flash(
            f"Reported time: {format_decimal(form.time_reported.data)}",
            "success"
        )

        return redirect(url_for("log_list"))

    return render_template("log_form.html", form=form)


# TODO: login required
@application.route("/update/<int:pk>/", methods=["GET", "POST"])
def log_update(pk: int):
    """Update existing time log entry"""

    log = TimeLogModel.query.get_or_404(pk)

    form = TimeLogForm()
    if form.validate_on_submit():
        log.task_id = int(form.task.data)
        log.value = form.time_reported.data
        log.date = form.date_reported.data

        db.session.add(log)
        db.session.commit()
        flash("Time report has been updated", "success")

        return redirect(url_for("log_list"))

    return render_template("log_form.html", form=form)


# TODO: login required
@application.route("/delete/<int:pk>/", methods=["GET", "POST"])
def log_delete(pk: int):
    """Delete existing time log entry"""

    log = TimeLogModel.query.get_or_404(pk)
    if request.method == "POST":
        db.session.delete(log)
        db.session.commit()
        flash("Time log has been deleted", "success")

        return redirect(url_for("log_list"))

    return render_template("log_delete.html", object=log)


if __name__ == "__main__":
    application.run()
