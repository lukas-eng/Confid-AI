from fastapi import APIRouter, UploadFile, File, Form
from controllers.interview_controller import procesar_respuesta_voz

router = APIRouter()

# ... (tus otras rutas)

@router.post("/responder-voz")
async def responder_por_voz(
    audio: UploadFile = File(...), 
    historial: str = Form(...) # Recibimos el historial como string JSONificado
):
    return procesar_respuesta_voz(audio, historial)