from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.database import Base, engine
from app.routers import employees, projects, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TaskManager API",
    description="TASK MANAGER API (&CRUD)",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(projects.router)
app.include_router(employees.router)
app.include_router(tasks.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
