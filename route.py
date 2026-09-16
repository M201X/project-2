from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import get_session
from dependencies import get_current_user, require_roles
from enums import Priority, Role, Status
from model import (User,Task,UserCreateRequest, TokenResponse,TaskCreate,TaskUpdate,TaskPublic,UserPublic)
from security import (hash_password,verify_password,create_access_token,)

router = APIRouter()

@router.post("/auth/register",response_model=UserPublic,status_code=201)

def register(data: UserCreateRequest,session: Session = Depends(get_session)):

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=Role.user,
        is_active=True
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@router.post("/auth/login",response_model=TokenResponse)

def login(form_data: OAuth2PasswordRequestForm = Depends(),session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )

@router.get( "/auth/me", response_model=UserPublic)

def me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.post("/tasks",response_model=TaskPublic,status_code=201)

def create_task(data: TaskCreate,current_user: User = Depends(get_current_user),session: Session = Depends(get_session)):
    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        status=Status.todo,
        user_id=current_user.id
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task

@router.get( "/tasks", response_model=list[TaskPublic])

def list_tasks(
    status: Status | None = None,
    priority: Priority | None = None,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    query = select(Task)

    if current_user.role != Role.admin:
        query = query.where(
            Task.user_id == current_user.id
        )

    if status is not None:
        query = query.where(
            Task.status == status
        )

    if priority is not None:
        query = query.where(
            Task.priority == priority
        )

    return session.exec(query.offset(skip).limit(limit)).all()

@router.get("/tasks/{task_id}",response_model=TaskPublic)

def get_task(task_id: int,current_user: User = Depends(get_current_user),session: Session = Depends(get_session)):

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

@router.patch( "/tasks/{task_id}", response_model=TaskPublic)

def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
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

    updates = data.model_dump(
        exclude_unset=True
    )

    for field, value in updates.items():
        setattr(task, field, value)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task

@router.patch("/tasks/{task_id}/complete",response_model=TaskPublic)

def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
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

    if task.status == Status.done:
        raise HTTPException(
            status_code=400,
            detail="Task is already completed"
        )

    task.status = Status.done

    session.add(task)
    session.commit()
    session.refresh(task)

    return task

@router.delete("/tasks/{task_id}",status_code=204)

def delete_task(
    task_id: int,
    current_user: User = Depends(
        require_roles([Role.admin])
    ),
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()

    return None
