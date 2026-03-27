from fastapi import HTTPException
import os
import uuid
import traceback
import random
from groq import Groq
from dotenv import load_dotenv
from services.gemini_service import procesar_audio_entrevista
from services.voice_service import texto_a_audio

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ============================================
# CONTADOR DE SILENCIOS POR SESIÓN
# Clave: algún identificador de sesión (aquí usamos una variable global simple)
# Si llega a 3 silencios consecutivos sin respuesta → entrevista finalizada
# ============================================

MAX_SILENCIOS = 3
_contador_silencios = 0  # se reinicia cuando el usuario responde normalmente


# ============================================
# PROCESAR RESPUESTA DE VOZ NORMAL
# ============================================

def procesar_respuesta_voz(archivo, historial_str: str, segundos_restantes: int = 900):
    global _contador_silencios

    temp_audio_path = None
    try:
        # 1. Guardar el archivo temporalmente
        temp_audio_path = f"temp_audio/{uuid.uuid4()}.webm"
        with open(temp_audio_path, "wb") as buffer:
            buffer.write(archivo.file.read())

        # Log legible del tiempo restante
        minutos = segundos_restantes // 60
        segundos = segundos_restantes % 60
        if segundos_restantes <= 60:
            print(f"⏰ TIEMPO RESTANTE: {segundos_restantes}s — Luvani cerrará la entrevista")
        elif segundos_restantes <= 180:
            print(f"⏰ TIEMPO RESTANTE: {minutos}m {segundos}s — Luvani comenzará a cerrar")
        else:
            print(f"⏰ TIEMPO RESTANTE: {minutos}m {segundos}s")

        print("⏳ Enviando audio a Gemini para transcripción y respuesta...")

        # 2. Procesar con Gemini
        resultado_gemini = procesar_audio_entrevista(
            temp_audio_path,
            historial_str,
            segundos_restantes=segundos_restantes
        )

        texto_usuario         = resultado_gemini.get("transcripcion_usuario", "")
        respuesta_gemini      = resultado_gemini.get("respuesta_entrevistador", "")
        analisis_voz          = resultado_gemini.get("analisis_voz", {})
        entrevista_finalizada = resultado_gemini.get("entrevista_finalizada", False)

        # El usuario respondió → reiniciar contador de silencios
        _contador_silencios = 0
        print(f"🔄 Contador de silencios reiniciado → {_contador_silencios}/{MAX_SILENCIOS}")

        print("✅ Usuario dijo:", texto_usuario)
        print("✅ Gemini respondió:", respuesta_gemini)
        print("🎤 ANALISIS DE VOZ:", analisis_voz)
        print("🏁 Entrevista finalizada:", entrevista_finalizada)

        # 3. Convertir a Audio
        print("⏳ Convirtiendo texto a voz con gTTS...")

        if isinstance(respuesta_gemini, dict):
            respuesta_gemini = " ".join(str(v) for v in respuesta_gemini.values())
        elif isinstance(respuesta_gemini, list):
            respuesta_gemini = " ".join(str(v) for v in respuesta_gemini)
        else:
            respuesta_gemini = str(respuesta_gemini)

        if not respuesta_gemini or respuesta_gemini.strip() == "":
            respuesta_gemini = "Gracias por tu respuesta. Continuemos con la siguiente pregunta."

        ruta_audio_respuesta = texto_a_audio(respuesta_gemini)
        print("✅ Audio guardado en:", ruta_audio_respuesta)

        return {
            "texto_usuario": texto_usuario,
            "respuesta_texto": respuesta_gemini,
            "audio_url": ruta_audio_respuesta,
            "analisis_voz": analisis_voz,
            "entrevista_finalizada": entrevista_finalizada
        }

    except Exception as e:
        print("\n💥 --- ERROR EXACTO EN EL BACKEND --- 💥")
        print(f"El error es: {str(e)}")
        traceback.print_exc()
        print("--------------------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except:
                pass


# ============================================
# BANCO DE RESPUESTAS DE SILENCIO
# ============================================

RESPUESTAS_SILENCIO = [
    "Seguimos en línea. Necesito que respondas para continuar con la entrevista.",
    "Llevamos un momento en silencio. ¿Vas a continuar con la entrevista?",
    "Te recuerdo que estamos en medio de una sesión. Por favor responde cuando puedas.",
    "Aún estoy aquí. La entrevista sigue activa, necesito tu respuesta.",
    "No he recibido respuesta. Si tienes alguna duda sobre la pregunta, dímelo.",
    "Estamos perdiendo tiempo. Por favor responde para avanzar.",
    "La entrevista continúa. Te espero para seguir con la siguiente pregunta.",
    "Si necesitas un momento está bien, pero necesito que retomes la conversación pronto.",
]

MENSAJE_CIERRE_SILENCIO = (
    "Hemos tenido varios minutos sin respuesta de tu parte. "
    "Voy a dar por finalizada la entrevista. "
    "Si deseas reagendar, puedes contactar al equipo de selección. Hasta luego."
)


# ============================================
# PROCESAR SILENCIO
# Acumula silencios — al llegar a 3, cierra la entrevista
# ============================================

def procesar_silencio(historial_str: str, segundos_restantes: int = 900):
    global _contador_silencios

    try:
        _contador_silencios += 1
        print(f"🔇 Silencio #{_contador_silencios}/{MAX_SILENCIOS} detectado")

        # ── CASO: 3 silencios consecutivos → cerrar entrevista ──
        if _contador_silencios >= MAX_SILENCIOS:
            print("🚨 Máximo de silencios alcanzado — cerrando entrevista")
            _contador_silencios = 0  # resetear para próxima sesión

            ruta_audio = texto_a_audio(MENSAJE_CIERRE_SILENCIO)
            print("✅ Audio de cierre por silencio guardado en:", ruta_audio)

            return {
                "respuesta_texto": MENSAJE_CIERRE_SILENCIO,
                "audio_url": ruta_audio,
                "entrevista_finalizada": True   # ← el frontend bloqueará el micrófono
            }

        # ── CASO: silencios 1 y 2 → Luvani reactiva ──
        referencia = random.choice(RESPUESTAS_SILENCIO)
        print(f"🎲 Referencia de silencio seleccionada: {referencia}")

        # En el segundo silencio el tono es más directo
        tono_extra = ""
        if _contador_silencios == 2:
            tono_extra = f"""
IMPORTANTE: Este es el segundo silencio consecutivo del candidato.
Sé más directa y firme. Hazle saber que si no responde la entrevista
podría darse por terminada. Sin amenazar, pero con claridad.
"""

        prompt = f"""
        Eres Luvani, entrevistadora de recursos humanos en una empresa de tecnología.
        Estás realizando una entrevista laboral a un candidato de ADSO.

        HISTORIAL DE LA CONVERSACIÓN:
        {historial_str}

        SITUACIÓN:
        El candidato lleva más de 1 minuto en silencio sin responder.
        Este es el silencio número {_contador_silencios} de {MAX_SILENCIOS}.

        REFERENCIA DE TONO (úsala como inspiración, no la copies literalmente):
        "{referencia}"

        {tono_extra}

        TU TAREA:
        - Di algo breve que recuerde al candidato que debe responder.
        - Adapta el mensaje al contexto de la conversación.
        - Sé directa y profesional. Nada de frases empáticas ni que quiten presión.
        - Máximo 2 oraciones. Sin listas. Tono neutro y formal.
        - NO uses "tómate tu tiempo", "no hay apuro" ni frases similares.
        - NO hagas una pregunta nueva. Solo recuérdale que debe responder.
        - Varía el mensaje, no repitas siempre lo mismo.

        Responde ÚNICAMENTE con lo que diría Luvani, sin explicaciones adicionales.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )

        respuesta_texto = response.choices[0].message.content
        print("✅ Luvani reactivó con:", respuesta_texto)

        ruta_audio = texto_a_audio(respuesta_texto)
        print("✅ Audio de silencio guardado en:", ruta_audio)

        return {
            "respuesta_texto": respuesta_texto,
            "audio_url": ruta_audio,
            "entrevista_finalizada": False
        }

    except Exception as e:
        print("\n💥 --- ERROR EN SILENCIO --- 💥")
        print(f"El error es: {str(e)}")
        traceback.print_exc()
        print("--------------------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PROCESAR REPORTE FINAL
# ============================================

def procesar_reporte_final(historial_str: str, metricas_voz_str: str):
    try:
        from services.gemini_service import generar_reporte_final
        print("⏳ Generando reporte final con Groq...")
        resultado = generar_reporte_final(historial_str, metricas_voz_str)
        print("✅ Reporte final generado con éxito")
        return resultado
    except Exception as e:
        print("\n💥 --- ERROR AL GENERAR REPORTE --- 💥")
        print(f"El error es: {str(e)}")
        traceback.print_exc()
        print("--------------------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))