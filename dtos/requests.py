from datetime import datetime, timezone

from pydantic import Field, field_validator
from sqlmodel import SQLModel

from enums import Priority


class UserCreateRequest(SQLModel):
    username: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=6)


class TaskCreateRequest(SQLModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None
    priority: Priority = Priority.medium
    due_date: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        if not value.strip():
            raise ValueError("TITLE_VALIDATION_17")

        return value

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: datetime | None):
        if value is None:
            return value

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)

        if value < datetime.now(timezone.utc):
            raise ValueError("Due date cannot be in the past")

        return value


class TaskUpdateRequest(SQLModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    description: str | None = None
    priority: Priority | None = None
    due_date: datetime | None = None
 
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None):
        if value is not None and not value.strip():
            raise ValueError("TITLE_VALIDATION_17")

        return value

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: datetime | None):
        if value is None:
            return value

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)

        if value < datetime.now(timezone.utc):
            raise ValueError("Due date cannot be in the past")

        return value