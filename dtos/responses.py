from datetime import datetime

from pydantic import BaseModel

from enums import Priority, Status, Role


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: Role
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    priority: Priority
    status: Status
    due_date: datetime | None
    created_at: datetime
    user_id: int