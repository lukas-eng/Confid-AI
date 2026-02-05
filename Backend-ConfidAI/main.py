from fastapi import FastAPI
from config.database import Base, engine
from routes.user_routes import router as user_router
from routes.auth_routes import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

# API Registro de usuarios 

app.include_router(user_router, prefix="/usuarios", tags=["Usuarios"])

# API Iniciar sesion 
app.include_router(auth_router, prefix="/auth", tags=["Auth"])