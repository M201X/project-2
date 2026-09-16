from sqlmodel import Session, SQLModel, create_engine
from config import settings
from model import User, Task


engine = create_engine(
    settings.database_url,
    echo=True,
    connect_args={
        "check_same_thread": False
    },
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

