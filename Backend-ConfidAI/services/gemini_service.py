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
# DETECTAR MULETILLAS (mejorado para español)
# ============================================

def detectar_muletillas(texto):
    """
    Detecta muletillas en español.
    Se usa lookahead/lookbehind con espacios y puntuación
    en lugar de \\b que falla con vocales acentuadas.
    """
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
        r"(?<!\w)o(?!\w) sea",
        r"(?<!\w)tipo(?!\w)",          # "tipo" como muletilla
        r"(?<!\w)osea(?!\w)",          # sin espacio
        r"básicamente",
        r"basicamente",
        r"(?<!\w)igual(?!\w)",         # "igual" como muletilla
        r"(?<!\w)eso(?!\w)",
        r"(?<!\w)claro(?!\w)",
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

    # NERVIOSISMO
    if pausa > 3 or muletillas > 4:
        resultado["nivel_nerviosismo"] = "Alto"
    elif pausa > 1.5 or muletillas > 2:
        resultado["nivel_nerviosismo"] = "Medio"
    else:
        resultado["nivel_nerviosismo"] = "Bajo"

    # FLUIDEZ
    if velocidad < 1 or tartamudeo > 2:
        resultado["fluidez"] = "Baja"
    elif velocidad < 2.5:
        resultado["fluidez"] = "Normal"
    else:
        resultado["fluidez"] = "Alta"

    # CLARIDAD
    resultado["claridad"] = "Respuesta poco desarrollada" if es_corta else "Explicación clara"

    # SEGURIDAD
    if pausa > 2.5 or muletillas > 3:
        resultado["seguridad"] = "Baja"
    elif pausa > 1:
        resultado["seguridad"] = "Media"
    else:
        resultado["seguridad"] = "Alta"

    return resultado


# ============================================
# DETECTAR SI ES UN SALUDO
# ============================================

def es_saludo(texto):
    """Detecta si el texto es principalmente un saludo sin contenido adicional."""
    texto_lower = texto.lower().strip()
    saludos = [
        "hola", "buenos días", "buenas tardes", "buenas noches",
        "buenas", "hey", "hi", "qué tal", "que tal", "cómo estás",
        "como estas", "hola!", "hola,", "hey!", "hola buenas"
    ]
    # Si el texto es muy corto Y contiene un saludo, es solo saludo
    palabras = texto_lower.split()
    if len(palabras) <= 4:
        for saludo in saludos:
            if saludo in texto_lower:
                return True
    return False


# ============================================
# LIMPIAR TRANSCRIPCION
# ============================================

def limpiar_transcripcion(texto):
    """Elimina timestamps tipo subtítulo."""
    texto = re.sub(r"\d{2}:\d{2}:\d{2}:\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}:\d{3}", "", texto)
    texto = texto.replace("\n", " ").strip()
    return texto


# ============================================
# INICIAR ENTREVISTA
# ============================================

def iniciar_entrevista_adso(nombre_estudiante):
    prompt = f"""
    Eres un entrevistador de recursos humanos llamado Andrés, trabajas en una empresa de tecnología.
    Vas a entrevistar a {nombre_estudiante}, un estudiante de Análisis y Desarrollo de Software (ADSO).

    Empieza la entrevista de forma natural y humana:
    - Salúdalo por su nombre
    - Preséntate brevemente
    - Di algo corto para romper el hielo (una frase, no más)
    - Luego haz una primera pregunta sencilla para conocerlo (no técnica aún)

    Sé cálido, directo y natural. No uses listas ni puntos. Habla como una persona real.
    """
    response = model.generate_content(prompt)
    return response.text


# ============================================
# GENERAR SIGUIENTE PREGUNTA
# ============================================

def generar_siguiente_pregunta(historial_conversacion, respuesta_estudiante):
    prompt = f"""
    Eres Andrés, un entrevistador humano de recursos humanos en una empresa tech.
    Estás haciendo una entrevista laboral a un candidato ADSO (Análisis y Desarrollo de Software).

    Historial de la conversación:
    {historial_conversacion}

    Última respuesta del candidato:
    "{respuesta_estudiante}"

    Tu tarea:
    1. Haz un comentario breve y natural sobre lo que dijo (como lo haría una persona real).
    2. Luego haz la siguiente pregunta. Puede ser personal, técnica, actitudinal o de proyectos.
    3. No uses listas, bullets ni formatos. Solo texto natural.
    4. Varía los temas conforme avanza la conversación.
    5. Sé cercano pero profesional.
    """
    response = model.generate_content(prompt)
    return response.text


# ============================================
# PROCESAR AUDIO DE ENTREVISTA
# ============================================

def procesar_audio_entrevista(audio_path, historial_conversacion):

    analisis_audio = analizar_audio_basico(audio_path)
    pausa_maxima = detectar_pausas(audio_path)

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    audio_part = {
        "mime_type": "audio/webm",
        "data": audio_data
    }

    # Obtener la última pregunta del entrevistador para contexto
    ultima_pregunta = ""
    if historial_conversacion:
        if isinstance(historial_conversacion, list):
            # Buscar el último mensaje del entrevistador
            for item in reversed(historial_conversacion):
                if isinstance(item, dict) and item.get("rol") == "entrevistador":
                    ultima_pregunta = item.get("mensaje", "")
                    break
                elif isinstance(item, str) and "Entrevistador:" in item:
                    ultima_pregunta = item.split("Entrevistador:")[-1].strip()
                    break
        elif isinstance(historial_conversacion, str):
            lineas = historial_conversacion.strip().split("\n")
            for linea in reversed(lineas):
                if "Entrevistador:" in linea or "Andrés:" in linea:
                    ultima_pregunta = linea.split(":")[-1].strip()
                    break

    prompt = f"""
    Eres Andrés, un entrevistador humano de recursos humanos en una empresa de tecnología.
    Estás realizando una entrevista laboral a un candidato de ADSO (Análisis y Desarrollo de Software).

    CONTEXTO DE LA CONVERSACIÓN:
    {historial_conversacion}

    DATOS DEL AUDIO:
    - Duración de la respuesta: {analisis_audio["duracion"]} segundos
    - Pausa más larga detectada: {pausa_maxima} segundos

    TU PERSONALIDAD:
    - Eres cercano, profesional y empático.
    - Hablas como una persona real, no como un robot.
    - Escuchas activamente y reaccionas a lo que dice el candidato.
    - Adaptas el tono: si el candidato está nervioso, lo tranquilizas.
    - No usas listas, ni bullets, ni formatos raros. Solo texto natural.

    REGLAS CLAVE:
    1. Si el candidato SOLO saluda (sin más contenido), responde al saludo de forma cálida
       y luego haz UNA pregunta sencilla para romper el hielo. NO saltes a preguntas técnicas.
    2. Si la respuesta es demasiado corta o vaga, pídele amablemente que desarrolle más,
       como lo haría un entrevistador real ("Interesante, ¿podrías contarme un poco más sobre eso?").
    3. Si la respuesta NO tiene nada que ver con la pregunta que hiciste, menciónalo de forma
       natural y educada, como: "Mmm, creo que me fui por las ramas, te pregunté sobre X,
       ¿me puedes hablar de eso?" — No seas brusco.
    4. Si la respuesta tiene relación, haz un comentario breve y natural, y continúa con
       la siguiente pregunta. No repitas la respuesta del candidato textualmente.
    5. NUNCA hagas más de una pregunta a la vez.
    6. Varía los temas: empieza con preguntas personales/motivacionales, luego técnicas,
       luego de proyectos, luego actitudinales.

    TAREA:
    1. Transcribe EXACTAMENTE lo que dijo el candidato en el audio.
    2. Genera tu respuesta como entrevistador (siguiendo las reglas anteriores).

    Devuelve ÚNICAMENTE este JSON, sin texto adicional ni backticks:
    {{
        "transcripcion_usuario": "",
        "respuesta_entrevistador": ""
    }}
    """

    try:
        response = model.generate_content([prompt, audio_part])
        clean_text = response.text.strip()

        # Limpiar markdown si viene con backticks
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        resultado = json.loads(clean_text.strip())

        # Limpiar transcripción
        texto_usuario = resultado.get("transcripcion_usuario", "")
        texto_usuario = limpiar_transcripcion(texto_usuario)
        resultado["transcripcion_usuario"] = texto_usuario

        # ============================================
        # ANALISIS DE VOZ (solo para métricas internas)
        # ============================================
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

        # NOTA: Ya NO sobreescribimos respuesta_entrevistador con mensajes hardcodeados.
        # El LLM maneja todo el flujo conversacional de forma natural según las reglas del prompt.

        return resultado

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e