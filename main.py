from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models import *
from app.core.database import engine
from app.routes import search_route, user_document_route, user_route, auth_route, file_route, folder_route, otp_route, favorites_route
from app.schemas.api_response import APIResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

Base.metadata.create_all(engine)

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True, 
    allow_methods=["*"],  
    allow_headers=["*"], 
)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            code=exc.detail["code"],
            result=None,
            message="An error occurred",
            error_message=exc.detail["message"]
        ).model_dump()
    )

app.include_router(auth_route.router)
app.include_router(user_route.router)
app.include_router(file_route.router)
app.include_router(folder_route.router)
app.include_router(otp_route.router)
app.include_router(favorites_route.router)
app.include_router(search_route.router)
app.include_router(user_document_route.router)