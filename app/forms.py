from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CreateProject(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    description = StringField(label="Description", validators=[DataRequired()])
    submit = SubmitField("Save")


class CreateTask(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    description = StringField(label="Description", validators=[DataRequired()])
    status = SelectField(label="status", choices=["todo", "in_progress", "done"], validators=[DataRequired()])
    priority = SelectField(label="Priority", choices=["low", "medium", "high"], validators=[DataRequired()])
    due_date = StringField(label="Date", validators=[DataRequired()])
    project_id = SelectField(label="Project", choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField("Add Task")
