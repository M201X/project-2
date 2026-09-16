from sqlmodel import Session
from database import engine
from enums import Role
from model import User
from security import hash_password


username = input("Username: ")
email = input("Email: ")
password = input("Password: ")


with Session(engine) as session:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=Role.admin,
        is_active=True
    )

    session.add(user)
    session.commit()

    print("Admin created successfully")
