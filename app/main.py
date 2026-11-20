from fastapi import FastAPI

from app.routers import task

app = FastAPI(title="Todo App")

app.include_router(router=task.router)
