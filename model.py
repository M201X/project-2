from datetime import datetime
from sqlmodel import Field, SQLModel
from enums import Priority, Status, Role
from pydantic import field_validator

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None
    priority: Priority = Priority.medium
    status: Status = Status.todo
    due_date: datetime | None = None
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        if not value.strip():
            raise ValueError("TITLE_VALIDATION_17")

        return value

class Task(TaskBase, table=True):
    id: int | None = Field(default=None,primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now )
    user_id: int


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"sqlite_autoincrement": True}
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    role: Role = Field(default=Role.user)
    is_active: bool = Field(default=True)

class UserCreateRequest(SQLModel):
    username: str
    email: str
    password: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    due_date: datetime | None = None
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None):
        if value is not None and not value.strip():
            raise ValueError("TITLE_VALIDATION_17")

        return value

class UserPublic(SQLModel):
    id: int
    username: str
    email: str
    role: Role
    is_active: bool

class TokenResponse(SQLModel):
    access_token: str
    token_type: str

class TaskPublic(SQLModel):
    id: int
    title: str
    description: str | None
    priority: Priority
    status: Status
    due_date: datetime | None
    created_at: datetime
    user_id: int
