from fastapi import FastAPI
from config.database import Base, engine
from routes.user_routes import router as user_router
from routes.auth_routes import router as auth_router
from routes import interview_routes
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()


app.include_router(user_router)
app.include_router(user_router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(interview_routes.router, prefix="/interview", tags=["Interview"])

os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
