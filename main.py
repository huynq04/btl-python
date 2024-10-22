from fastapi import FastAPI
from app.models import *
from app.core.database import engine
from app.routes import user_route, auth_route

app = FastAPI()

Base.metadata.create_all(engine)

app.include_router(auth_route.router)
app.include_router(user_route.router)
app.include_router(file_route.router)
