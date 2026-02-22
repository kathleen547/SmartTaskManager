
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from flask_login import UserMixin
from .extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False, default='user')

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    assigned_tasks: Mapped[list["Task"]] = relationship("Task", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name} role={self.role}>"



class Project(db.Model):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship("Task",back_populates="project",cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project id={self.id} title={self.title}>"



class Task(db.Model):
    __tablename__ = "tasks"

    VALID_STATUSES = ['todo', 'in_progress', 'done']
    VALID_PRIORITIES = ['low', 'medium', 'high']

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default='todo')
    priority: Mapped[str] = mapped_column(String(100), nullable=False, default='medium')
    due_date: Mapped[str] = mapped_column(String(250), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("projects.id"), nullable=False)
    assigned_user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=True)
    owner: Mapped["User"] = relationship("User", back_populates="assigned_asks")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title} status={self.status}>"



@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


