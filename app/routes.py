from flask import Blueprint, request, redirect, url_for, render_template, flash
from .forms import RegisterForm, LoginForm, CreateProject, CreateTask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user
from .extensions import db
from .models import User, Task, Project
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route("/", methods=["GET", "POST"])
def home_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")
        checked_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if checked_user is not None:
            if check_password_hash(checked_user.password, password):
                login_user(checked_user)
                return redirect(url_for('main.get_content'))
            else:
                flash(message="Incorrect password, try again")
                return redirect(url_for('main.home_login'))
        else:
            flash(message="There's no such user. Please register")
            return redirect(url_for('main.home_login'))
    return render_template("index.html", form=form, current_user=current_user)



@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user_email = request.form.get("email")
        new_user_password = request.form.get("password")
        new_user_name = request.form.get("name")
        new_user_hashed_password = generate_password_hash(new_user_password, method='pbkdf2', salt_length=8)
        checked_user = db.session.execute(db.select(User).where(User.email == new_user_email)).scalar()
        if checked_user is not None:
            flash(message="You've already signed up with that email. Log In instead")
            return redirect(url_for('main.home_login'))
        else:
            new_user = User(name=new_user_name, email=new_user_email, password=new_user_hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("main.get_content"))
    return render_template("register.html", form=form, current_user=current_user)



@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home_login"))


@main.route('/dashboard')
def get_content():
    tasks_to_filter = db.select(Task).where(Task.assigned_user_id == current_user.id and Task.priority == 'todo')
    todo_number = db.session.scalar(db.select(func.count()).select_from(tasks_to_filter))

    to_filter = db.select(Project).where(Project.owner_id == current_user.id)
    project_number = db.session.scalar(db.select(func.count()).select_from(to_filter))
    return render_template("dashboard.html", current_user=current_user, data=project_number, data1=todo_number)


@main.route('/new-project', methods=["GET", "POST"])
def add_new_project():
    form = CreateProject()
    new_id=current_user.id
    if form.validate_on_submit():
        new_project = Project(
            title=form.title.data,
            description=form.description.data,
            owner_id= new_id
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('main.get_all_projects'))
    return render_template("make-project.html", form=form, current_user=current_user)


@main.route('/projects', methods=["GET"])
def get_all_projects():
    result = db.session.execute(db.select(Project).where(Project.owner_id == current_user.id))
    projects = result.scalars().all()
    return render_template("projects.html", projects= projects, current_user=current_user)


@main.route('/new-task', methods=["GET", "POST"])
def add_new_task():
    form = CreateTask()
    result = db.session.execute(db.select(Project).where(Project.owner_id == current_user.id))
    projects = result.scalars().all()
    form.project_id.choices = [p.id for p in projects]
    if form.validate_on_submit():
        task_user_id = current_user.id

        new_task = Task(
            title= form.title.data,
            description= form.description.data,
            status= form.status.data,
            priority= form.priority.data,
            due_date= form.due_date.data,
            project_id=form.project_id.data,
            assigned_user_id= task_user_id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('main.get_all_tasks'))
    return render_template("make-task.html", form=form, current_user=current_user)


@main.route('/my-tasks', methods=["GET"])
def get_all_tasks():
    result = db.session.execute(db.select(Task).where(Task.assigned_user_id == current_user.id))
    tasks = result.scalars().all()
    return render_template("my-tasks.html", tasks=tasks, current_user=current_user)

