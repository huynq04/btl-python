from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models import *
from app.core.database import engine
from app.routes import user_route, auth_route
from app.schemas.api_response import APIResponse

app = FastAPI()

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            code=exc.status_code,
            result=None,
            message="An error occurred",
            error_message=exc.detail
        ).model_dump()
    )


Base.metadata.create_all(engine)

app.include_router(auth_route.router)
app.include_router(user_route.router)

