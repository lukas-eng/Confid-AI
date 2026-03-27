from fastapi import APIRouter, UploadFile, File, Form
from controllers.interview_controller import procesar_respuesta_voz, procesar_silencio

router = APIRouter()


@router.post("/responder-voz")
async def responder_por_voz(
    audio: UploadFile = File(...),
    historial: str = Form(...),
    segundos_restantes: int = Form(900)
):
    return procesar_respuesta_voz(audio, historial, segundos_restantes)


@router.post("/silencio")
async def avisar_silencio(
    historial: str = Form(...),
    segundos_restantes: int = Form(900)
):
    
    return procesar_silencio(historial, segundos_restantes)




@router.post("/generar-reporte")
async def generar_reporte(
    historial: str = Form(...),
    metricas_voz: str = Form(...)
):
    from controllers.interview_controller import procesar_reporte_final
    return procesar_reporte_final(historial, metricas_voz)