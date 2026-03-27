from groq import Groq
import os
import json
from dotenv import load_dotenv
import librosa
import numpy as np
import re
from concurrent.futures import ThreadPoolExecutor

# ============================================
# CONFIGURAR GROQ
# ============================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("🚨 ALERTA: No se encontró GROQ_API_KEY. Revisa tu archivo .env")

client = Groq(api_key=groq_api_key)


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
# BANCO DE PREGUNTAS POR FASE
#
#  Fase 1 — PERSONAL     : min  0 →  3  (seg 900 → 720)  ~2 preguntas
#  Fase 2 — MOTIVACIONAL : min  3 →  6  (seg 720 → 540)  ~2 preguntas
#  Fase 3 — TÉCNICA      : min  6 → 10  (seg 540 → 300)  ~3 preguntas
#  Fase 4 — PROYECTOS    : min 10 → 13  (seg 300 → 120)  ~2 preguntas
#  Fase 5 — ACTITUDINAL  : min 13 → 14  (seg 120 →  60)  ~1-2 preguntas
#  CIERRE                : últimos 60s  — despedida
# ============================================

BANCO_PREGUNTAS = {

    "personal": [
        "¿Qué fue lo que te llevó a elegir la carrera de Análisis y Desarrollo de Software?",
        "¿Cómo describirías tu trayectoria hasta llegar a estudiar ADSO?",
        "¿Qué es lo que más te gusta del área de desarrollo de software?",
        "¿Tienes algún referente o persona que haya influido en tu interés por la tecnología?",
        "¿Cómo equilibras tus estudios con otras responsabilidades o actividades?",
    ],

    "motivacional": [
        "¿Por qué te interesa trabajar en una empresa de tecnología?",
        "¿Dónde te ves profesionalmente en los próximos dos o tres años?",
        "¿Qué tipo de proyectos o retos te gustaría enfrentar en tu primer empleo?",
        "¿Qué te motivó a postularte a esta posición en particular?",
        "¿Qué esperas aprender en un entorno laboral que no puedas aprender en la academia?",
    ],

    "tecnica": [
        "¿Con qué lenguajes de programación te sientes más cómodo trabajando actualmente?",
        "¿Puedes explicarme qué es una API REST y para qué se usa?",
        "¿Cuál es la diferencia entre una base de datos relacional y una no relacional?",
        "¿Qué herramientas de control de versiones has usado? ¿Cómo describes tu experiencia con Git?",
        "¿Qué es el patrón MVC y en qué situaciones lo has aplicado?",
        "¿Cómo manejarías un error inesperado en producción que afecta a los usuarios?",
        "¿Qué frameworks o librerías has explorado por tu cuenta fuera de la academia?",
        "¿Qué entiendes por código limpio y por qué es importante?",
    ],

    "proyectos": [
        "¿Puedes contarme sobre algún proyecto académico o personal que hayas desarrollado?",
        "¿Cuál ha sido el proyecto más complejo en el que has participado y cuál fue tu rol?",
        "¿Has trabajado en equipo para desarrollar software? ¿Cómo fue esa experiencia?",
        "¿Alguna vez tuviste que resolver un problema técnico difícil en un proyecto? ¿Qué hiciste?",
        "¿Tienes proyectos personales, repositorios en GitHub o algo que hayas construido por iniciativa propia?",
    ],

    "actitudinal": [
        "¿Cómo reaccionas cuando recibes una crítica sobre tu trabajo o tu código?",
        "¿Qué haces cuando te atascas en un problema y no encuentras la solución?",
        "¿Cómo te adaptas cuando cambian los requisitos de un proyecto en medio del desarrollo?",
        "¿Prefieres trabajar de forma independiente o en equipo? ¿Por qué?",
        "¿Cómo manejas la presión cuando tienes varios entregables al mismo tiempo?",
        "¿Qué harías si no estás de acuerdo con una decisión técnica tomada por tu equipo?",
    ],
}


# ============================================
# DETERMINAR FASE SEGÚN TIEMPO RESTANTE
# ============================================

def _determinar_fase(segundos_restantes: int) -> dict:
    if segundos_restantes > 720:
        return {
            "nombre": "PERSONAL",
            "numero": 1,
            "rango": "minutos 0 a 3",
            "objetivo": "Romper el hielo y conocer al candidato como persona",
            "preguntas": BANCO_PREGUNTAS["personal"]
        }
    elif segundos_restantes > 540:
        return {
            "nombre": "MOTIVACIONAL",
            "numero": 2,
            "rango": "minutos 3 a 6",
            "objetivo": "Entender sus motivaciones, metas y expectativas laborales",
            "preguntas": BANCO_PREGUNTAS["motivacional"]
        }
    elif segundos_restantes > 300:
        return {
            "nombre": "TÉCNICA",
            "numero": 3,
            "rango": "minutos 6 a 10",
            "objetivo": "Evaluar conocimientos técnicos de programación y herramientas",
            "preguntas": BANCO_PREGUNTAS["tecnica"]
        }
    elif segundos_restantes > 120:
        return {
            "nombre": "PROYECTOS",
            "numero": 4,
            "rango": "minutos 10 a 13",
            "objetivo": "Conocer su experiencia práctica y trabajo en equipo",
            "preguntas": BANCO_PREGUNTAS["proyectos"]
        }
    else:
        return {
            "nombre": "ACTITUDINAL",
            "numero": 5,
            "rango": "minutos 13 a 14",
            "objetivo": "Evaluar comportamiento, valores y soft skills",
            "preguntas": BANCO_PREGUNTAS["actitudinal"]
        }


# ============================================
# BLOQUE DE FASE PARA EL PROMPT
# ============================================

def _bloque_fase(segundos_restantes: int) -> str:
    fase = _determinar_fase(segundos_restantes)
    preguntas_formateadas = "\n".join(f"  - {p}" for p in fase["preguntas"])

    return f"""
📋 FASE ACTUAL: {fase["numero"]}/5 — {fase["nombre"]} ({fase["rango"]})
Objetivo de esta fase: {fase["objetivo"]}

PREGUNTAS DISPONIBLES — elige UNA que aún no hayas hecho en esta conversación:
{preguntas_formateadas}

INSTRUCCIÓN IMPORTANTE:
- Elige la pregunta que mejor fluya con lo que acaba de decir el candidato.
- Puedes reformularla ligeramente para que suene natural, pero sin cambiar su esencia.
- NO hagas preguntas de otras fases ni inventes preguntas fuera de esta lista.
- Si ya hiciste todas las preguntas de esta lista, haz una pregunta de profundización
  sobre algo que el candidato mencionó antes.
- NUNCA hagas más de una pregunta a la vez.
"""


# ============================================
# BLOQUE DE TIEMPO PARA EL PROMPT
# ============================================

def _bloque_tiempo(segundos_restantes: int) -> str:
    if segundos_restantes <= 60:
        return """
⏰ CIERRE OBLIGATORIO — Queda menos de 1 minuto de entrevista.
- NO hagas más preguntas bajo ninguna circunstancia.
- Agradece al candidato brevemente por su tiempo y disposición.
- Dile que el equipo revisará su perfil y que estarán en contacto pronto.
- Despídete de forma cordial y natural. Máximo 3 oraciones en total.
"""
    elif segundos_restantes <= 180:
        return """
⏰ AVISO — Quedan menos de 3 minutos de entrevista.
Ve cerrando la conversación con naturalidad.
Puedes hacer máximo UNA pregunta más antes de despedirte.
No abras temas nuevos.
"""
    else:
        return ""


# ============================================
# INICIAR ENTREVISTA — solo texto, sin audio
# ============================================

def iniciar_entrevista_adso(nombre_estudiante):
    prompt = f"""
    Eres Luvani, una entrevistadora de recursos humanos que trabaja en una empresa de tecnología.
    Vas a entrevistar a {nombre_estudiante}, estudiante de Análisis y Desarrollo de Software (ADSO).

    Este es el INICIO de la entrevista. El candidato aún no ha dicho nada.

    Haz lo siguiente en orden:
    1. Saluda a {nombre_estudiante} por su nombre de forma cordial pero profesional.
    2. Preséntate: di tu nombre (Luvani) y que eres del equipo de selección.
    3. Explica brevemente que van a tener una conversación para conocerlo mejor.
    4. Haz UNA sola pregunta inicial sencilla y personal (no técnica), por ejemplo
       sobre cómo llegó a estudiar ADSO o qué le gusta del área.

    Habla de corrido, como una persona real en un contexto laboral. Sin listas, sin bullets, sin formatos.
    Máximo 4-5 oraciones en total. Sé cordial y profesional, sin exagerar el entusiasmo.
    Evita frases muy efusivas como "¡Qué gusto conocerte!" o "¡Estoy muy emocionada!".
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    return response.choices[0].message.content


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
    1. Haz un comentario breve y neutral sobre lo que dijo (sin exagerar ni ser efusiva).
    2. Luego haz la siguiente pregunta. Puede ser personal, técnica, actitudinal o de proyectos.
    3. Sin listas, bullets ni formatos. Solo texto natural.
    4. Varía los temas conforme avanza la conversación.
    5. Sé cordial pero profesional. No efusiva.
    6. Evita frases como "¡Qué bien!", "¡Excelente!" o cualquier reacción exagerada.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    return response.choices[0].message.content


# ============================================
# PROCESAR AUDIO DE ENTREVISTA
# ============================================

def procesar_audio_entrevista(
    audio_path,
    historial_conversacion,
    es_primer_audio=False,
    nombre_estudiante="",
    segundos_restantes=900
):

    # PASO 1: Análisis de audio y transcripción EN PARALELO
    def transcribir():
        with open(audio_path, "rb") as f:
            return client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                response_format="text"
            )

    def analizar():
        return analizar_audio_basico(audio_path)

    def pausas():
        return detectar_pausas(audio_path)

    with ThreadPoolExecutor(max_workers=3) as executor:
        fut_transcripcion = executor.submit(transcribir)
        fut_analisis      = executor.submit(analizar)
        fut_pausas        = executor.submit(pausas)

        transcripcion  = fut_transcripcion.result()
        analisis_audio = fut_analisis.result()
        pausa_maxima   = fut_pausas.result()

    texto_usuario = limpiar_transcripcion(transcripcion)

    # PASO 2: Construir bloques dinámicos del prompt

    bloque_presentacion = ""
    if es_primer_audio:
        bloque_presentacion = f"""
    ⚠️ IMPORTANTE — PRIMER MENSAJE DEL CANDIDATO:
    Este es el primer audio del candidato. Antes de responder a lo que dijo,
    DEBES presentarte primero como Luvani:
    - Saluda a {nombre_estudiante} por su nombre de forma cordial.
    - Di que eres Luvani, del equipo de selección.
    - Di que van a tener una conversación para conocerlo mejor.
    - Luego responde naturalmente a lo que dijo el candidato.
    - Cierra con UNA pregunta inicial sencilla y personal (no técnica aún).
    Todo en máximo 5 oraciones, de corrido, sin listas. Sin exagerar el entusiasmo.
    """

    bloque_tiempo = _bloque_tiempo(segundos_restantes)
    bloque_fase   = _bloque_fase(segundos_restantes) if segundos_restantes > 60 else ""

    # Log de fase en terminal
    if segundos_restantes > 60:
        fase_actual = _determinar_fase(segundos_restantes)
        print(f"📋 FASE ACTIVA: {fase_actual['numero']}/5 — {fase_actual['nombre']} ({fase_actual['rango']})")

    prompt = f"""
    Eres Luvani, una entrevistadora de recursos humanos en una empresa de tecnología.
    Estás realizando una entrevista laboral a un candidato de ADSO.

    {bloque_presentacion}

    HISTORIAL DE LA CONVERSACIÓN:
    {historial_conversacion}

    DATOS DEL AUDIO:
    - Duración de la respuesta: {analisis_audio["duracion"]} segundos
    - Pausa más larga detectada: {pausa_maxima} segundos

    LO QUE DIJO EL CANDIDATO:
    "{texto_usuario}"

    {bloque_fase}

    {bloque_tiempo}

    TU PERSONALIDAD:
    - Eres profesional, cordial y directa.
    - Hablas como una persona real en un contexto laboral formal.
    - Escuchas lo que dice el candidato y respondes de forma natural, sin exagerar reacciones.
    - Si el candidato está nervioso o no sabe qué responder, lo reconoces brevemente
      con una frase corta ("No te preocupes, tómate tu tiempo" o "Tranquilo, no hay
      apuro") y sigues adelante. No profundices en ello ni lo conviertas en un momento
      emocional.
    - Sin listas, bullets ni formatos. Solo texto natural.

    REGLAS DE CONVERSACIÓN:
    1. Si el candidato SOLO saluda, respóndele el saludo de forma cordial y haz UNA
       pregunta sencilla para romper el hielo. NO saltes a preguntas técnicas.
    2. Si la respuesta es muy corta o vaga, pídele que amplíe con una frase simple
       y neutral ("¿Puedes contarme un poco más sobre eso?").
    3. Si la respuesta no tiene nada que ver con la pregunta anterior, redirige con
       naturalidad y sin drama.
    4. Si el candidato dice que está nervioso o que no sabe qué responder, dile
       algo breve y neutro como "No te preocupes, tómate tu tiempo" o "Tranquilo,
       es normal" — y luego repite o reformula la pregunta. No hagas más comentarios
       sobre eso.
    5. NUNCA hagas más de una pregunta a la vez.
    6. NUNCA uses frases muy efusivas como "¡Qué interesante!", "¡Excelente respuesta!"
       o "¡Me alegra mucho escuchar eso!". Reacciona con naturalidad y mesura.
    7. SIEMPRE respeta la fase activa. No mezcles categorías entre fases.

    Responde ÚNICAMENTE con tu respuesta como Luvani, sin explicaciones adicionales.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )

    respuesta_luvani = response.choices[0].message.content

    # PASO 3: Métricas
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

    entrevista_finalizada = segundos_restantes <= 60

    return {
        "transcripcion_usuario": texto_usuario,
        "respuesta_entrevistador": respuesta_luvani,
        "entrevista_finalizada": entrevista_finalizada,
        "fase_actual": _determinar_fase(segundos_restantes)["nombre"] if segundos_restantes > 60 else "CIERRE",
        "analisis_voz": {
            "duracion_respuesta": analisis_audio["duracion"],
            "pausa_maxima": pausa_maxima,
            "velocidad_palabras_segundo": velocidad,
            "respuesta_corta": es_corta,
            "muletillas_detectadas": muletillas_detectadas,
            "posible_tartamudeo": tartamudeo_detectado,
            "evaluacion_comportamiento": evaluacion
        }
    }