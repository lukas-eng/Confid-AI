import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import os
import uuid

# Crear carpeta temporal para audios si no existe
os.makedirs("temp_audio", exist_ok=True)

def transcribir_audio(archivo_audio):
    r = sr.Recognizer()
    
    # Generar nombre único y convertir a WAV (formato compatible)
    filename = f"temp_audio/{uuid.uuid4()}"
    input_path = f"{filename}.webm"  # Asumimos que llega en webm del navegador
    wav_path = f"{filename}.wav"
    
    # Guardar el archivo temporalmente
    with open(input_path, "wb") as buffer:
        buffer.write(archivo_audio.file.read())
        
    # Convertir a WAV usando pydub
    audio = AudioSegment.from_file(input_path)
    audio.export(wav_path, format="wav")
    
    # Transcribir
    with sr.AudioFile(wav_path) as source:
        audio_data = r.record(source)
        try:
            texto = r.recognize_google(audio_data, language="es-ES")
        except sr.UnknownValueError:
            texto = "No pude entender lo que dijiste, ¿puedes repetir?"
        except sr.RequestError:
            texto = "Error en el servicio de reconocimiento de voz."

    # Limpieza de archivos
    os.remove(input_path)
    os.remove(wav_path)
    
    return texto

def texto_a_audio(texto):
    tts = gTTS(text=texto, lang='es')
    filename = f"response_{uuid.uuid4()}.mp3"
    filepath = f"static/audio/{filename}" # Asegúrate de tener esta carpeta o configurar static files
    
    # Crear carpeta si no existe
    os.makedirs("static/audio", exist_ok=True)
    
    tts.save(filepath)
    return filepath  # Retornamos la ruta para que el front la reproduzca