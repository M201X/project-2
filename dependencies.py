from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from database import get_session
from model import User, Task
from security import read_user_id_from_token
from enums import Role


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    try:
        user_id = read_user_id_from_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User is inactive"
        )

    return user


def require_roles(*allowed_roles: Role):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission"
            )

        return current_user

    return role_checker

def get_task_or_404(task_id: int,current_user: User,session: Session):

    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if (
        current_user.role != Role.admin
        and task.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task