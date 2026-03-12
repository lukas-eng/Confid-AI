import os
import uuid
import asyncio
import edge_tts

# Crear carpetas necesarias
os.makedirs("temp_audio", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

# Voz colombiana natural de Microsoft Edge
VOZ = "es-CO-SalomeNeural"

async def _generar_audio(texto: str, filepath: str):
    communicate = edge_tts.Communicate(texto, voice=VOZ)
    await communicate.save(filepath)

def texto_a_audio(texto: str) -> str:
    """
    Convierte texto en voz usando Edge TTS (Microsoft).
    Voz: es-CO-SalomeNeural (español colombiano, natural).
    Devuelve la ruta relativa al archivo generado.
    """
    filename = f"response_{uuid.uuid4()}.mp3"
    filepath = f"static/audio/{filename}"

    asyncio.run(_generar_audio(texto, filepath))

    return filepath