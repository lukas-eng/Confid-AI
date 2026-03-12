import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import librosa
import numpy as np
import re

# ============================================
# CONFIGURAR GEMINI
# ============================================

load_dotenv()

mi_api_key = os.getenv("GEMINI_API_KEY")

if not mi_api_key:
    raise ValueError("🚨 ALERTA: No se encontró GEMINI_API_KEY. Revisa tu archivo .env")

genai.configure(api_key=mi_api_key)

model = genai.GenerativeModel('gemini-2.0-flash')


# ============================================
# ANALISIS BASICO DEL AUDIO
# ============================================

def analizar_audio_basico(audio_path):
    y, sr = librosa.load(audio_path)
    duracion = librosa.get_duration(y=y, sr=sr)
    energia = np.mean(np.abs(y))
    return {
        "duracion": round(duracion, 2),
        "energia": float(energia)
    }


# ============================================
# DETECTAR PAUSAS
# ============================================

def detectar_pausas(audio_path):
    y, sr = librosa.load(audio_path)
    intervalos = librosa.effects.split(y, top_db=20)
    pausas = []
    for i in range(len(intervalos) - 1):
        pausa = (intervalos[i+1][0] - intervalos[i][1]) / sr
        pausas.append(pausa)
    if pausas:
        return round(max(pausas), 2)
    return 0


# ============================================
# VELOCIDAD DE RESPUESTA
# ============================================

def velocidad_respuesta(texto, duracion):
    palabras = len(texto.split())
    if duracion == 0:
        return 0
    return round(palabras / duracion, 2)


# ============================================
# RESPUESTA MUY CORTA
# ============================================

def respuesta_corta(texto):
    palabras = len(texto.split())
    return palabras < 5


# ============================================
# DETECTAR MULETILLAS
# ============================================

def detectar_muletillas(texto):
    muletillas = [
        r"(?<!\w)eh(?!\w)",
        r"(?<!\w)ehh(?!\w)",
        r"(?<!\w)ehhh(?!\w)",
        r"(?<!\w)emm(?!\w)",
        r"(?<!\w)mmm(?!\w)",
        r"(?<!\w)este(?!\w)",
        r"(?<!\w)pues(?!\w)",
        r"o sea",
        r"digamos",
        r"como que",
        r"(?<!\w)bueno(?!\w)",
        r"(?<!\w)tipo(?!\w)",
        r"(?<!\w)osea(?!\w)",
        r"básicamente",
        r"basicamente",
        r"(?<!\w)igual(?!\w)",
        r"la verdad",
        r"en realidad",
    ]
    texto_lower = texto.lower()
    contador = 0
    for patron in muletillas:
        coincidencias = re.findall(patron, texto_lower)
        contador += len(coincidencias)
    return contador


# ============================================
# DETECTAR TARTAMUDEO
# ============================================

def detectar_tartamudeo(texto):
    palabras = texto.lower().split()
    repeticiones = 0
    for i in range(len(palabras) - 1):
        if palabras[i] == palabras[i+1] and len(palabras[i]) > 1:
            repeticiones += 1
    return repeticiones


# ============================================
# EVALUACION DEL COMPORTAMIENTO
# ============================================

def evaluar_comportamiento_voz(duracion, pausa, velocidad, es_corta, muletillas, tartamudeo):
    resultado = {}

    if pausa > 3 or muletillas > 4:
        resultado["nivel_nerviosismo"] = "Alto"
    elif pausa > 1.5 or muletillas > 2:
        resultado["nivel_nerviosismo"] = "Medio"
    else:
        resultado["nivel_nerviosismo"] = "Bajo"

    if velocidad < 1 or tartamudeo > 2:
        resultado["fluidez"] = "Baja"
    elif velocidad < 2.5:
        resultado["fluidez"] = "Normal"
    else:
        resultado["fluidez"] = "Alta"

    resultado["claridad"] = "Respuesta poco desarrollada" if es_corta else "Explicación clara"

    if pausa > 2.5 or muletillas > 3:
        resultado["seguridad"] = "Baja"
    elif pausa > 1:
        resultado["seguridad"] = "Media"
    else:
        resultado["seguridad"] = "Alta"

    return resultado


# ============================================
# LIMPIAR TRANSCRIPCION
# ============================================

def limpiar_transcripcion(texto):
    texto = re.sub(r"\d{2}:\d{2}:\d{2}:\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}:\d{3}", "", texto)
    texto = texto.replace("\n", " ").strip()
    return texto


# ============================================
# INICIAR ENTREVISTA — solo texto, sin audio
# Se llama UNA sola vez al comenzar la sesión
# ============================================

def iniciar_entrevista_adso(nombre_estudiante):
    """
    Genera el saludo inicial de Luvani ANTES de que el candidato diga nada.
    Llamar esto desde el endpoint de inicio de sesión, no desde el de audio.
    """
    prompt = f"""
    Eres Luvani, una entrevistadora de recursos humanos que trabaja en una empresa de tecnología.
    Vas a entrevistar a {nombre_estudiante}, estudiante de Análisis y Desarrollo de Software (ADSO).

    Este es el INICIO de la entrevista. El candidato aún no ha dicho nada.

    Haz lo siguiente en orden:
    1. Saluda a {nombre_estudiante} por su nombre de forma cálida.
    2. Preséntate: di tu nombre (Luvani) y que eres del equipo de selección.
    3. Explica brevemente que van a tener una conversación para conocerlo mejor.
    4. Rompe el hielo con UNA frase corta y amigable.
    5. Haz UNA sola pregunta inicial sencilla y personal (no técnica), por ejemplo
       sobre cómo está, cómo llegó a estudiar ADSO, o qué le gusta del área.

    Habla de corrido, como una persona real. Sin listas, sin bullets, sin formatos.
    Máximo 4-5 oraciones en total. Sé cálida y natural.
    """
    response = model.generate_content(prompt)
    return response.text


# ============================================
# GENERAR SIGUIENTE PREGUNTA
# ============================================

def generar_siguiente_pregunta(historial_conversacion, respuesta_estudiante):
    prompt = f"""
    Eres Luvani, entrevistadora de recursos humanos en una empresa tech.
    Estás haciendo una entrevista laboral a un candidato ADSO.

    Historial de la conversación:
    {historial_conversacion}

    Última respuesta del candidato:
    "{respuesta_estudiante}"

    Tu tarea:
    1. Haz un comentario breve y natural sobre lo que dijo.
    2. Luego haz la siguiente pregunta. Puede ser personal, técnica, actitudinal o de proyectos.
    3. Sin listas, bullets ni formatos. Solo texto natural.
    4. Varía los temas conforme avanza la conversación.
    5. Sé cercana pero profesional.
    """
    response = model.generate_content(prompt)
    return response.text


# ============================================
# PROCESAR AUDIO DE ENTREVISTA
# ============================================

def procesar_audio_entrevista(audio_path, historial_conversacion, es_primer_audio=False, nombre_estudiante=""):
    """
    Parámetros nuevos:
    - es_primer_audio: True si es el primer mensaje de voz del candidato.
    - nombre_estudiante: nombre del candidato, necesario solo si es_primer_audio=True.

    Flujo:
    - Si es_primer_audio=True: Luvani primero se presenta y luego responde al audio.
    - Si es_primer_audio=False: flujo normal de conversación.
    """

    analisis_audio = analizar_audio_basico(audio_path)
    pausa_maxima = detectar_pausas(audio_path)

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    audio_part = {
        "mime_type": "audio/webm",
        "data": audio_data
    }

    # Bloque de presentación: solo se incluye en el primer audio
    bloque_presentacion = ""
    if es_primer_audio:
        bloque_presentacion = f"""
    ⚠️ IMPORTANTE — PRIMER MENSAJE DEL CANDIDATO:
    Este es el primer audio del candidato. Antes de responder a lo que dijo,
    DEBES presentarte primero como Luvani:
    - Saluda a {nombre_estudiante} por su nombre.
    - Di que eres Luvani, del equipo de selección.
    - Di que van a tener una conversación para conocerlo mejor.
    - Luego responde naturalmente a lo que dijo el candidato.
    - Cierra con UNA pregunta inicial sencilla y personal (no técnica aún).
    Todo en máximo 5 oraciones, de corrido, sin listas.
    """

    prompt = f"""
    Eres Luvani, una entrevistadora humana de recursos humanos en una empresa de tecnología.
    Estás realizando una entrevista laboral a un candidato de ADSO.

    {bloque_presentacion}

    HISTORIAL DE LA CONVERSACIÓN:
    {historial_conversacion}

    DATOS DEL AUDIO:
    - Duración de la respuesta: {analisis_audio["duracion"]} segundos
    - Pausa más larga detectada: {pausa_maxima} segundos

    TU PERSONALIDAD:
    - Eres cercana, profesional y empática.
    - Hablas como una persona real, no como un robot.
    - Escuchas activamente y reaccionas a lo que dice el candidato.
    - Adaptas el tono: si el candidato está nervioso, lo tranquilizas.
    - Sin listas, bullets ni formatos. Solo texto natural.

    REGLAS DE CONVERSACIÓN:
    1. Si el candidato SOLO saluda, respóndele el saludo con calidez y haz UNA pregunta
       sencilla para romper el hielo. NO saltes a preguntas técnicas.
    2. Si la respuesta es muy corta o vaga, pídele amablemente que amplíe más.
    3. Si la respuesta no tiene nada que ver con la pregunta anterior, menciónalo con
       naturalidad y redirige: "Creo que me perdí un poco, te había preguntado sobre X,
       ¿me cuentas sobre eso?"
    4. Si la respuesta es relevante, comenta brevemente y haz la siguiente pregunta.
    5. NUNCA hagas más de una pregunta a la vez.
    6. Progresión de temas: personal/motivacional → técnico → proyectos → actitudinal.

    TAREA:
    1. Transcribe EXACTAMENTE lo que dijo el candidato en el audio.
    2. Genera tu respuesta como Luvani (siguiendo todo lo anterior).

    Devuelve ÚNICAMENTE este JSON, sin texto adicional ni backticks:
    {{
        "transcripcion_usuario": "",
        "respuesta_entrevistador": ""
    }}
    """

    try:
        response = model.generate_content([prompt, audio_part])
        clean_text = response.text.strip()

        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        resultado = json.loads(clean_text.strip())

        texto_usuario = resultado.get("transcripcion_usuario", "")
        texto_usuario = limpiar_transcripcion(texto_usuario)
        resultado["transcripcion_usuario"] = texto_usuario

        # Métricas de voz
        velocidad = velocidad_respuesta(texto_usuario, analisis_audio["duracion"])
        es_corta = respuesta_corta(texto_usuario)
        muletillas_detectadas = detectar_muletillas(texto_usuario)
        tartamudeo_detectado = detectar_tartamudeo(texto_usuario)

        evaluacion = evaluar_comportamiento_voz(
            analisis_audio["duracion"],
            pausa_maxima,
            velocidad,
            es_corta,
            muletillas_detectadas,
            tartamudeo_detectado
        )

        resultado["analisis_voz"] = {
            "duracion_respuesta": analisis_audio["duracion"],
            "pausa_maxima": pausa_maxima,
            "velocidad_palabras_segundo": velocidad,
            "respuesta_corta": es_corta,
            "muletillas_detectadas": muletillas_detectadas,
            "posible_tartamudeo": tartamudeo_detectado,
            "evaluacion_comportamiento": evaluacion
        }

        return resultado

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e