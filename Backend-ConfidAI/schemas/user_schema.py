from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: str
    password: str
