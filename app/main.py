from fastapi import FastAPI
from app.core.config import settings
from app.api.router import router
from app import models
from app.database.connector import engine
from fastapi.middleware.cors import CORSMiddleware
models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title=settings.APP_NAME
)
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://103.145.78.48",
    "http://103.145.78.48:5101"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router=router, prefix=settings.API_VERSION)