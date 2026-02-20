import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Forzar a Python a leer el archivo .env
load_dotenv()

# 2. Extraer la llave
mi_api_key = os.getenv("GEMINI_API_KEY")

# Pequeño chequeo de seguridad
if not mi_api_key:
    raise ValueError("🚨 ALERTA: No se encontró GEMINI_API_KEY. Revisa tu archivo .env")

# 3. Configurar la IA
genai.configure(api_key=mi_api_key)

# 🕵️‍♀️ RASTREADOR: Imprimir los modelos que tu llave SÍ tiene permitidos
print("\n--- MODELOS DISPONIBLES EN TU CUENTA ---")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"✅ {m.name}")
print("----------------------------------------\n")

# Inicializar el modelo
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def iniciar_entrevista_adso(nombre_estudiante):
    prompt = f"Actúa como un entrevistador amigable pero profesional para un estudiante de Análisis y Desarrollo de Software (ADSO) llamado {nombre_estudiante}. Hazle la primera pregunta para romper el hielo y evaluar sus habilidades blandas."
    
    response = model.generate_content(prompt)
    return response.text

def generar_siguiente_pregunta(historial_conversacion, respuesta_estudiante):
    prompt = f"Eres un entrevistador para un perfil junior de desarrollo de software (ADSO). Basado en este historial: {historial_conversacion} y la última respuesta del candidato: '{respuesta_estudiante}', evalúa brevemente su respuesta y haz la siguiente pregunta técnica o situacional."
    
    response = model.generate_content(prompt)
    return response.text