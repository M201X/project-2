from datetime import datetime
from sqlmodel import Field, SQLModel
from enums import Priority, Role, Status

class User(SQLModel, table=True):

    __tablename__ = "users"
    __table_args__ = {"sqlite_autoincrement": True}

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    username: str
    email: str
    hashed_password: str
    role: Role = Field(
        default=Role.user
    )

    is_active: bool = Field(
        default=True
    )


class Task(SQLModel, table=True):

    __tablename__ = "tasks"
    __table_args__ = {"sqlite_autoincrement": True}

    id: int | None = Field(default=None,primary_key=True)
    title: str
    description: str | None = None

    priority: Priority = Field(
        default=Priority.medium
    )

    status: Status = Field(
        default=Status.todo
    )

    due_date: datetime | None = None

    created_at: datetime = Field(
        default_factory=datetime.now
    )

    user_id: int = Field(
        foreign_key="users.id"
    )