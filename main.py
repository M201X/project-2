from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables
from routerss.auth import router as auth_router
from routerss.tasks import router as tasks_router
@asynccontextmanager
async def lifespan(app: FastAPI):

    create_db_and_tables()

    yield
app = FastAPI(
    title="Task API",
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/")
def read_root():
    return {"message": "Hello, backend world!"}
