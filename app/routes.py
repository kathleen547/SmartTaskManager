"""
Main Blueprint containing all application routes for authentication,
dashboard, project management, and task management.
"""

from flask import Blueprint, request, redirect, url_for, render_template, flash
from .forms import RegisterForm, LoginForm, CreateProject, CreateTask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user
from .extensions import db
from .models import User, Task, Project
from sqlalchemy import func, case, or_
from datetime import date

# Initialize the main Blueprint for route registration
main = Blueprint('main', __name__)


# ─────────────────────────────────────────────
#  AUTHENTICATION ROUTES
# ─────────────────────────────────────────────

@main.route("/", methods=["GET", "POST"])
def home_login():
    """
    Home page and login handler.

    GET:  Renders the login form.
    POST: Validates credentials, logs in the user if correct,
          or flashes an appropriate error message.
    """
    form = LoginForm()

    if form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")

        # Look up user by email in the database
        checked_user = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar()

        if checked_user is not None:
            # Verify hashed password against provided input
            if check_password_hash(checked_user.password, password):
                login_user(checked_user)
                return redirect(url_for('main.get_content'))
            else:
                flash(message="Incorrect password, try again")
                return redirect(url_for('main.home_login'))
        else:
            # No account found with that email
            flash(message="There's no such user. Please register")
            return redirect(url_for('main.home_login'))

    return render_template("index.html", form=form, current_user=current_user)


@main.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration handler.

    GET:  Renders the registration form.
    POST: Validates form data, checks for duplicate email,
          creates a new user with a hashed password, and logs them in.
    """
    form = RegisterForm()

    if form.validate_on_submit():
        new_user_email = request.form.get("email")
        new_user_password = request.form.get("password")
        new_user_name = request.form.get("name")

        # Hash the password before storing it (pbkdf2 with salt)
        new_user_hashed_password = generate_password_hash(
            new_user_password, method='pbkdf2', salt_length=8
        )

        # Check if a user with this email already exists
        checked_user = db.session.execute(
            db.select(User).where(User.email == new_user_email)
        ).scalar()

        if checked_user is not None:
            # Prevent duplicate accounts
            flash(message="You've already signed up with that email. Log In instead")
            return redirect(url_for('main.home_login'))
        else:
            # Create and persist new user, then log them in immediately
            new_user = User(
                name=new_user_name,
                email=new_user_email,
                password=new_user_hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("main.get_content"))

    return render_template("register.html", form=form, current_user=current_user)


@main.route('/logout')
@login_required  # Only authenticated users can log out
def logout():
    """Logs out the current user and redirects to the login page."""
    logout_user()
    return redirect(url_for('main.home_login'))


# ─────────────────────────────────────────────
#  DASHBOARD ROUTE
# ─────────────────────────────────────────────

@main.route('/dashboard')
def get_content():
    """
    User dashboard page.

    Displays a summary including:
    - Total number of user's projects
    - Total number of todo tasks assigned to the user
    - A prioritized list of up to 10 urgent/overdue tasks

    Tasks are ordered by urgency:
      1. Overdue tasks (due_date < today, not done)
      2. Due today tasks (not done)
      3. In-progress tasks
      4. Everything else
    """
    # Count tasks assigned to the user with 'todo' status
    tasks_todo_to_filter = db.select(Task).where(
        Task.assigned_user_id == current_user.id, Task.status == 'todo'
    )
    todo_number = db.session.scalar(
        db.select(func.count()).select_from(tasks_todo_to_filter)
    )
    # Count tasks assigned to the user with 'done' status
    tasks_completed_to_filter = db.select(Task).where(
        Task.assigned_user_id == current_user.id, Task.status == 'done'
    )
    completed_number = db.session.scalar(
        db.select(func.count()).select_from(tasks_completed_to_filter)
    )
    # Count tasks not completed by today
    tasks_overdue_to_filter = db.select(Task).where(
        Task.assigned_user_id == current_user.id, Task.due_date < date.today(), Task.status != 'done'
    )
    overdue_number = db.session.scalar(
        db.select(func.count()).select_from(tasks_overdue_to_filter)
    )
    # Count projects owned by the current user
    to_filter = db.select(Project).where(Project.owner_id == current_user.id)
    project_number = db.session.scalar(
        db.select(func.count()).select_from(to_filter)
    )

    today = date.today()

    # Define custom ordering: overdue → due today → in progress → rest
    priority_order = case(
        ((Task.due_date < today) & (Task.status != "done"), 1),
        ((Task.due_date == today) & (Task.status != "done"), 2),
        (Task.status == "in_progress", 3),
        else_=4
    )

    # Fetch up to 10 urgent/relevant tasks for the dashboard widget
    task_table = db.session.scalars(
        db.select(Task)
        .where(
            Task.assigned_user_id == current_user.id,
            or_(
                ((Task.due_date < today) & (Task.status != "done")),
                ((Task.due_date == today) & (Task.status != "done")),
                (Task.status == "in_progress")
            )
        )
        .order_by(priority_order, Task.due_date.asc())
        .limit(10)
    ).all()

    return render_template(
        "dashboard.html",
        current_user=current_user,
        data=project_number,  # Total projects count
        data1=todo_number,  # Total todo tasks count
        data2=completed_number, # Total completed tasks count
        data3=overdue_number, # Total overdue tasks count
        dashboard_table=task_table  # Prioritized task list
    )


# ─────────────────────────────────────────────
#  PROJECT ROUTES
# ─────────────────────────────────────────────

@main.route('/new-project', methods=["GET", "POST"])
def add_new_project():
    """
    Create a new project.

    GET:  Renders the project creation form.
    POST: Validates the form and saves the new project to the database,
          assigning it to the currently logged-in user.
    """
    form = CreateProject()
    new_id = current_user.id  # Associate project with the current user

    if form.validate_on_submit():
        new_project = Project(
            title=form.title.data,
            description=form.description.data,
            owner_id=new_id
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('main.get_all_projects'))

    return render_template("make-project.html", form=form, current_user=current_user)


@main.route('/projects', methods=["GET"])
def get_all_projects():
    """
    Display all projects owned by the current user.

    Fetches and lists all projects where the owner matches
    the currently authenticated user.
    """
    result = db.session.execute(
        db.select(Project).where(Project.owner_id == current_user.id)
    )
    projects = result.scalars().all()
    return render_template("projects.html", projects=projects, current_user=current_user)


@main.route("/project/<int:project_id>", methods=["GET", "POST"])
def show_project(project_id):
    """
    Display a single project's detail page with task statistics.

    Shows the project details along with a breakdown of task counts:
    - Total tasks
    - Todo tasks
    - In-progress tasks
    - Completed tasks
    - Overdue tasks (past due date and not done)

    Args:
        project_id (int): The ID of the project to display.
    """
    # Fetch project or return 404 if not found
    requested_project = db.get_or_404(Project, project_id)

    # Total task count for this project
    total = db.session.scalar(
        db.select(func.count())
        .select_from(Task)
        .where(Task.project_id == project_id)
    )

    # Count tasks with 'todo' status
    todo = db.session.scalar(
        db.select(func.count())
        .select_from(Task)
        .where(Task.project_id == project_id, Task.status == "todo")
    )

    # Count tasks currently being worked on
    in_progress = db.session.scalar(
        db.select(func.count())
        .select_from(Task)
        .where(Task.project_id == project_id, Task.status == "in_progress")
    )

    # Count tasks that have been completed
    completed = db.session.scalar(
        db.select(func.count())
        .select_from(Task)
        .where(Task.project_id == project_id, Task.status == "done")
    )

    # Count tasks past their due date that are not yet completed
    overdue = db.session.scalar(
        db.select(func.count())
        .select_from(Task)
        .where(
            Task.project_id == project_id,
            Task.due_date < date.today(),
            Task.status != "done"
        )
    )

    return render_template(
        "project.html",
        project=requested_project,
        data1=total,
        data2=todo,
        data3=in_progress,
        data4=completed,
        data5=overdue,
        current_user=current_user
    )


@main.route("/edit-project/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    """
    Edit an existing project's details.

    GET:  Pre-populates the form with existing project data.
    POST: Validates and saves the updated project information.

    Args:
        project_id (int): The ID of the project to edit.
    """
    # Fetch the project to edit, or return 404
    project = db.get_or_404(Project, project_id)

    # Pre-fill the form with current project data
    edit_form = CreateProject(
        title=project.title,
        description=project.description
    )
    edit_form.submit.label.text = "Save"  # Change button label for edit context

    if edit_form.validate_on_submit():
        project.title = edit_form.title.data
        project.description = edit_form.description.data
        db.session.commit()
        return redirect(url_for('main.show_project', project_id=project_id))

    return render_template(
        'make-project.html',
        form=edit_form,
        is_Edit=True,
        project_id=project_id,
        current_user=current_user
    )


# ─────────────────────────────────────────────
#  TASK ROUTES
# ─────────────────────────────────────────────

@main.route('/new-task', methods=["GET", "POST"])
def add_new_task():
    """
    Create a new task.

    GET:  Renders the task creation form with the user's projects
          populated in the project dropdown.
    POST: Validates the form and saves the new task, assigning it
          to the current user.
    """
    projects = db.session.scalars(
        db.select(Project).where(Project.owner_id == current_user.id)
    ).all()

    if not projects:
        return render_template("make-task.html", current_user=current_user, no_projects=True)
    else:
        form = CreateTask()
        # Load current user's projects for the project selector dropdown
        result = db.session.execute(
            db.select(Project).where(Project.owner_id == current_user.id)
        )
        projects = result.scalars().all()
        form.project_id.choices = [(p.id, p.title) for p in projects]

        if form.validate_on_submit():
            task_user_id = current_user.id
            new_task = Task(
                title=form.title.data,
                description=form.description.data,
                status=form.status.data,
                priority=form.priority.data,
                due_date=form.due_date.data,
                project_id=form.project_id.data,
                assigned_user_id=task_user_id
            )
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('main.get_all_tasks'))

        return render_template("make-task.html", form=form, current_user=current_user)


@main.route('/edit-task/<int:task_id>', methods=["GET", "POST"])
def edit_task(task_id):
    """
    Edit an existing task.

    GET:  Pre-fills the form with the current task data and loads
          the user's projects for the project dropdown.
    POST: Validates and saves the updated task data, then redirects
          to the parent project's detail page.

    Args:
        task_id (int): The ID of the task to edit.
    """
    # Fetch the task or return 404 if not found
    task = db.get_or_404(Task, task_id)

    # Pre-populate form with existing task values
    edit_form = CreateTask(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id
    )

    # Populate project dropdown with (id, title) tuples for display
    user_projects = db.session.scalars(
        db.select(Project).where(Project.owner_id == current_user.id)
    ).all()
    edit_form.project_id.choices = [(project.id, project.title) for project in user_projects]

    # Update submit button text to reflect edit context
    edit_form.submit.label.text = "Save Changes"

    if edit_form.validate_on_submit():
        # Apply updated values to the existing task record
        task.title = edit_form.title.data
        task.description = edit_form.description.data
        task.status = edit_form.status.data
        task.priority = edit_form.priority.data
        task.due_date = edit_form.due_date.data
        task.project_id = edit_form.project_id.data
        db.session.commit()
        # Redirect back to the project that contains this task
        return redirect(url_for('main.show_project', project_id=task.project_id))

    return render_template(
        'make-task.html',
        form=edit_form,
        is_Edit=True,
        task=task,
        current_user=current_user
    )


@main.route('/my-tasks', methods=["GET"])
def get_all_tasks():
    """
    Display all tasks assigned to the current user.

    Fetches all tasks where assigned_user_id matches
    the currently authenticated user.
    """
    result = db.session.execute(
        db.select(Task).where(Task.assigned_user_id == current_user.id)
    )
    tasks = result.scalars().all()
    return render_template("my-tasks.html", tasks=tasks, current_user=current_user)


@main.route("/delete/<int:task_id>")
def delete_task(task_id):
    """
    Delete a task by its ID.

    Fetches the task, stores its parent project ID for redirect,
    deletes the task, and redirects back to the parent project page.

    Args:
        task_id (int): The ID of the task to delete.
    """
    task_to_delete = db.get_or_404(Task, task_id)

    # Save project_id before deletion for redirect
    project_id = task_to_delete.project_id

    db.session.delete(task_to_delete)
    db.session.commit()

    # Return user to the project the deleted task belonged to
    return redirect(url_for('main.show_project', project_id=project_id))
