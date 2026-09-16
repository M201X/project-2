from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from database import get_session
from dependencies import get_current_user, get_task_or_404,require_roles
from enums import Priority, Status, Role
from model import User, Task
from dtos.requests import (
    TaskCreateRequest,
    TaskUpdateRequest,
)
from dtos.responses import TaskResponse


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post(
    "",
    response_model=TaskResponse,
    status_code=201,
    summary="Create a task"
)
def create_task(
    data: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
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

@router.get(
    "",
    response_model=list[TaskResponse],
    summary="List tasks"
)
def list_tasks(
    status: Status | None = Query(
        default=None
    ),
    priority: Priority | None = Query(
        default=None
    ),
    skip: int = Query(
        default=0,
        ge=0
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

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

   
    query = query.offset(skip).limit(limit)

    return session.exec(query).all()

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get one task"
)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = get_task_or_404(
        task_id,
        current_user,
        session
    )

    return task

@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task"
)
def update_task(
    task_id: int,
    data: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = get_task_or_404(
        task_id,
        current_user,
        session
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

@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Complete a task",
    description="Changes the task status to done."
)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = get_task_or_404(
        task_id,
        current_user,
        session
    )

    if task.status == Status.done:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Task is already completed"
        )

    task.status = Status.done

    session.add(task)
    session.commit()
    session.refresh(task)

    return task

@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Delete a task"
)
def delete_task(
    task_id: int,
    current_user: User = Depends(
        require_roles(Role.admin)
    ),
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)

    if task is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()

    return None
