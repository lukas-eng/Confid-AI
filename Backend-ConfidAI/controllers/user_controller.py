from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user_model import User
from services.auth_service import hash_password

def registrar_usuario(db: Session, data):
    existe = db.query(User).filter(User.correo == data.correo).first()
    if existe:
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    usuario = User(
        nombre=data.nombre,
        apellido=data.apellido,
        correo=data.correo,
        telefono=data.telefono,
        password=hash_password(data.password)
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": "Usuario registrado correctamente",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "correo": usuario.correo,
            "telefono": usuario.telefono
        }
    }
