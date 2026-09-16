from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables
from route import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI( title="Task API",lifespan=lifespan)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Hello, backend world!"}
