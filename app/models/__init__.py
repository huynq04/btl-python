from app.core.database import Base
from fastapi import FastAPI
from app.routes import user_route, auth_route, file_route
import app.models
app = FastAPI()

app.include_router(user_route.router)
app.include_router(auth_route.router)
app.include_router(file_route.router)

