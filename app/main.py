from fastapi import FastAPI

from app.api.routers import task, category

app = FastAPI(title="Todo App")

app.include_router(router=task.router)
app.include_router(router=category.router)
