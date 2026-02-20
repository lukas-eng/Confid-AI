from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from services.gemini_service import generar_siguiente_pregunta
from services.voice_service import transcribir_audio, texto_a_audio
import os

import traceback # Añade esto arriba en tus imports

def procesar_respuesta_voz(archivo: UploadFile, historial_str: str):
    try:
        # 1. Transcribir
        texto_usuario = transcribir_audio(archivo)
        print(f"✅ 1. Usuario dijo: {texto_usuario}") 
        
        # 2. Obtener respuesta de Gemini
        print("⏳ 2. Enviando mensaje a Gemini...")
        respuesta_gemini = generar_siguiente_pregunta(historial_str, texto_usuario)
        print(f"✅ Gemini respondió: {respuesta_gemini[:50]}...") # Imprime un pedacito
        
        # 3. Convertir a Audio
        print("⏳ 3. Convirtiendo texto a voz con gTTS...")
        ruta_audio_respuesta = texto_a_audio(respuesta_gemini)
        print("✅ 4. Audio guardado en:", ruta_audio_respuesta)
        
        return {
            "texto_usuario": texto_usuario,
            "respuesta_texto": respuesta_gemini,
            "audio_url": ruta_audio_respuesta 
        }

    except Exception as e:
        print("\n💥 --- ERROR EXACTO EN EL BACKEND --- 💥")
        print(f"El error es: {str(e)}")
        traceback.print_exc() # Esto nos dará la línea exacta del problema
        print("--------------------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))