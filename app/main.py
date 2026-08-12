from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.DB.db import db
import app.routes.auth as auth
import app.routes.faculty as faculty
import app.routes.student as student
@asynccontextmanager
async def lifespan(app:FastAPI):
    await db.connect()
    yield
    await db.close()
app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(faculty.router)
app.include_router(student.router)