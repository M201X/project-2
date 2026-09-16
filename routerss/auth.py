from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import get_session
from dependencies import get_current_user
from dtos.requests import UserCreateRequest
from dtos.responses import TokenResponse, UserResponse
from enums import Role
from model import User
from security import (hash_password, verify_password,create_access_token)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
def register(
    data: UserCreateRequest,
    session: Session = Depends(get_session)
):

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


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):

    user = session.exec(
        select(User).where(
            User.username == form_data.username
        )
    ).first()

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

    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User is inactive"
        )

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )

@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user: User = Depends(get_current_user)
):
    return current_user