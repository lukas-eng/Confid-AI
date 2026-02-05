from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.user_schema import UserCreate
from controllers.user_controller import registrar_usuario
from config.database import SessionLocal
from services.jwt_service import verificar_token
from fastapi import Depends


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/registro")
def registro(usuario: UserCreate, db: Session = Depends(get_db)):
    return registrar_usuario(db, usuario)

@router.get("/perfil")
def perfil_usuario(token_data: dict = Depends(verificar_token)):
    return {
        "mensaje": "Acceso autorizado",
        "token_data": token_data
    }
