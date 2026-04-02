"""
WTForms form definitions used for user input across the application.
All forms use Flask-WTF for CSRF protection.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    """
    Form for new user registration.

    Fields:
        name     (str): Full name of the user.
        email    (str): Email address (used as login identifier).
        password (str): Plain-text password (hashed before storage).
    """
    name = StringField(label="Name", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    """
    Form for existing user login.

    Fields:
        email    (str): Registered email address.
        password (str): Account password.
    """
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CreateProject(FlaskForm):
    """
    Form for creating or editing a project.

    Fields:
        title       (str): Project name (must be unique in the DB).
        description (str): Brief summary of the project.
    """
    title = StringField(label="Title", validators=[DataRequired()])
    description = StringField(label="Description", validators=[DataRequired()])
    submit = SubmitField("Create Project")


class CreateTask(FlaskForm):
    """
    Form for creating or editing a task.

    Fields:
        title       (str):  Task name.
        description (str):  Task details.
        status      (str):  Current state — choices: todo, in_progress, done.
        priority    (str):  Urgency level — choices: low, medium, high.
        due_date    (str):  Target completion date (e.g. YYYY-MM-DD).
        project_id  (int):  ID of the project this task belongs to.
                            Populated dynamically in routes before rendering.
    """
    title = StringField(label="Title", validators=[DataRequired()])
    description = StringField(label="Description", validators=[DataRequired()])

    # Predefined status choices matching Task.VALID_STATUSES
    status = SelectField(
        label="Status",
        choices=["todo", "in_progress", "done"],
        validators=[DataRequired()]
    )

    # Predefined priority choices matching Task.VALID_PRIORITIES
    priority = SelectField(
        label="Priority",
        choices=["low", "medium", "high"],
        validators=[DataRequired()]
    )

    due_date = StringField(label="Date", validators=[DataRequired()])

    # Choices populated dynamically in the route based on current user's projects
    project_id = SelectField(label="Project", choices=[], coerce=int, validators=[DataRequired()])

    submit = SubmitField("Add Task")