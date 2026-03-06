from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import uuid
import traceback
from services.gemini_service import procesar_audio_entrevista
from services.voice_service import texto_a_audio

def procesar_respuesta_voz(archivo: UploadFile, historial_str: str):
    temp_audio_path = None
    try:
        # 1. Guardar el archivo temporalmente
        temp_audio_path = f"temp_audio/{uuid.uuid4()}.webm"
        with open(temp_audio_path, "wb") as buffer:
            buffer.write(archivo.file.read())
            
        print("⏳ 1. Enviando audio a Gemini para transcripción y respuesta...")
        
        # 2. Procesar con Gemini (audio directo)
        resultado_gemini = procesar_audio_entrevista(temp_audio_path, historial_str)
        
        texto_usuario = resultado_gemini.get("transcripcion_usuario", "")
        respuesta_gemini = resultado_gemini.get("respuesta_entrevistador", "")
        analisis_voz = resultado_gemini.get("analisis_voz", {})

        print("✅ Usuario dijo:", texto_usuario)
        print("✅ Gemini respondió:", respuesta_gemini)
        print("🎤 ANALISIS DE VOZ:", analisis_voz)
        
        # 3. Convertir a Audio
        print("⏳ 3. Convirtiendo texto a voz con gTTS...")
        
        # Salvaguarda por si Gemini es terco y devuelve un dict o list anidado en lugar de string
        if isinstance(respuesta_gemini, dict):
            respuesta_gemini = " ".join(str(v) for v in respuesta_gemini.values())
        elif isinstance(respuesta_gemini, list):
            respuesta_gemini = " ".join(str(v) for v in respuesta_gemini)
        else:
            respuesta_gemini = str(respuesta_gemini)

        if not respuesta_gemini or respuesta_gemini.strip() == "":
            respuesta_gemini = "Gracias por tu respuesta. Continuemos con la siguiente pregunta."

        ruta_audio_respuesta = texto_a_audio(respuesta_gemini)
        print("✅ 4. Audio guardado en:", ruta_audio_respuesta)
        
        return {
            "texto_usuario": texto_usuario,
            "respuesta_texto": respuesta_gemini,
            "audio_url": ruta_audio_respuesta,
            "analisis_voz": analisis_voz
        }

    except Exception as e:
        print("\n💥 --- ERROR EXACTO EN EL BACKEND --- 💥")
        print(f"El error es: {str(e)}")
        traceback.print_exc()
        print("--------------------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Limpiar el archivo temporal local
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except:
                pass