"""
SQLAlchemy database models for the application.
Defines the User, Project, and Task tables and their relationships.
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from flask_login import UserMixin
from .extensions import db, login_manager
from datetime import date


class User(UserMixin, db.Model):
    """
    Represents an application user.

    Inherits from UserMixin to provide default Flask-Login implementations
    (is_authenticated, is_active, get_id, etc.).

    Relationships:
        - projects: One-to-many with Project (user owns many projects)
        - assigned_tasks: One-to-many with Task (user is assigned many tasks)
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)  # Must be unique across all users
    password: Mapped[str] = mapped_column(String(256), nullable=False)  # Stored as hashed value
    role: Mapped[str] = mapped_column(String(100), nullable=False, default='user')  # 'user' or 'admin'

    # One user → many projects (deletes projects if user is deleted)
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="owner", cascade="all, delete-orphan"
    )

    # One user → many assigned tasks
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="owner"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name} role={self.role}>"


class Project(db.Model):
    """
    Represents a project owned by a user.

    Each project can contain multiple tasks.

    Relationships:
        - owner: Many-to-one with User (project belongs to one user)
        - tasks: One-to-many with Task (project has many tasks)
    """
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)  # Project titles must be unique
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    # Foreign key linking project to its owning user
    owner_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))

    # Many projects → one user
    owner: Mapped["User"] = relationship("User", back_populates="projects")

    # One project → many tasks (deletes tasks if project is deleted)
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} title={self.title}>"


class Task(db.Model):
    """
    Represents a task within a project.

    Tasks can be assigned to users and tracked by status and priority.

    Class Attributes:
        VALID_STATUSES (list): Allowed values for the status field.
        VALID_PRIORITIES (list): Allowed values for the priority field.

    Relationships:
        - project: Many-to-one with Project (task belongs to one project)
        - owner: Many-to-one with User (task is assigned to one user)
    """
    __tablename__ = "tasks"

    # Allowed values for validation reference
    VALID_STATUSES = ['todo', 'in_progress', 'done']
    VALID_PRIORITIES = ['low', 'medium', 'high']

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default='todo')  # Default: todo
    priority: Mapped[str] = mapped_column(String(100), nullable=False, default='medium')  # Default: medium
    due_date: Mapped[date] = mapped_column(db.Date, nullable=False)

    # Foreign key linking task to its parent project (required)
    project_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("projects.id"), nullable=False)

    # Many tasks → one project
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")

    # Foreign key linking task to the assigned user (optional)
    assigned_user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=True)

    # Many tasks → one user (the assigned user)
    owner: Mapped["User"] = relationship("User", back_populates="assigned_tasks")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title} status={self.status}>"


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader callback.

    Called automatically by Flask-Login to reload the user object
    from the session on each request using the stored user ID.

    Args:
        user_id (int): The ID stored in the session.

    Returns:
        User: The corresponding User object, or 404 if not found.
    """
    return db.get_or_404(User, user_id)