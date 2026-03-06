from gtts import gTTS
import os
import uuid

# Crear carpeta temporal para audios si no existe
os.makedirs("temp_audio", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

def texto_a_audio(texto):
    """
    Convierte el texto en voz utilizando Google TTS.
    Devuelve la ruta relativa al archivo generado.
    """
    tts = gTTS(text=texto, lang='es')
    filename = f"response_{uuid.uuid4()}.mp3"
    filepath = f"static/audio/{filename}"
    
    tts.save(filepath)
    return filepath