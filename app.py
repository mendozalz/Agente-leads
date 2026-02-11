from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import os
import json
import gradio as gr

load_dotenv(override=True)
client_openai = OpenAI()

def registrar_datos_usuario(correo, nombre="No proporcionado", notas="No proporcionadas"):
    """Registra los datos del usuario interesado"""
    print(f"Registrando datos del usuario: \n Correo: {correo}, \n Nombre: {nombre}, \n Notas: {notas}")
    with open("contaxtos.txt", "a", encoding="utf-8") as f:
        f.write(f"Correo: {correo}, Nombre: {nombre}, Notas: {notas}\n")

    return {"registrado": "Exitoso"}

def registrar_pregunta_desconocida(pregunta):
    """Registra las preguntas que el modelo no pudo responder"""
    print(f"Registrando pregunta desconocida: {pregunta}")
    with open("preguntas_desconocidas.txt", "a", encoding="utf-8") as f:
        f.write(f"Pregiunta: {pregunta}\n")

    return {"registrado": "Exitoso"}

herramienta_registrar_datos_usuario = {
    "name": "registrar_datos_usuario",
    "description": "Registra los datos del usuario interesado en el producto o servicio. Recibe un correo electrónico obligatorio, un nombre opcional y notas adicionales opcionales.",
    "parameters": {
        "type": "object",
        "properties": {
            "correo": {
                "type": "string",
                "description": "Correo electrónico del usuario interesado (obligatorio)"
            },
            "nombre": {
                "type": "string",
                "description": "Nombre del usuario interesado (opcional)"
            },
            "notas": {
                "type": "string",
                "description": "Notas adicionales sobre el usuario interesado (opcional)"
            }
        },
        "required": ["correo"],
        "additionalProperties": False
    }
}

herramienta_pregunta_desconocida = {
    "name": "registrar_pregunta_desconocida",
    "description": "Registra las preguntas que el modelo no pudo responder para su posterior análisis y mejora. Recibe la pregunta que el modelo no pudo responder o que no esta en su base de conocimiento, aunque no te parezca relevante, es importante registrarla para mejorar el modelo en el futuro.",
    "parameters": {
        "type": "object",
        "properties": {
            "pregunta": {
                "type": "string",
                "description": "Pregunta que el modelo no pudo responder o que no esta en su base de conocimiento (obligatorio)"
            }
        },
        "required": ["pregunta"],
        "additionalProperties": False       
    }
}

herramientas = [
    {"type": "function", "function": herramienta_registrar_datos_usuario},
    {"type": "function", "function": herramienta_pregunta_desconocida}
]

 
def manejar_llamadas_herramientas(llamadas_herramientas):
    """Maneja las llamadas a las herramientas definidas"""
    respuestas = []
    for llamada in llamadas_herramientas:
        nombre_herramienta = llamada.function.name
        argumentos = json.loads(llamada.function.arguments)
        
        if nombre_herramienta == "registrar_datos_usuario":
            respuesta = registrar_datos_usuario(**argumentos)
        elif nombre_herramienta == "registrar_pregunta_desconocida":
            respuesta = registrar_pregunta_desconocida(**argumentos)
        else:
            respuesta = {"error": "Herramienta no reconocida"}
        
        respuestas.append({
            "role": "tool",
            "content": json.dumps(respuesta),
            "tool_call_id": llamada.id
        })
    
    return respuestas

lector = PdfReader("curriculum-lenin.pdf")
info_linkedin = ""
for pagina in lector.pages:
    texto = pagina.extract_text()
    if "linkedin.com" in texto:
        info_linkedin += texto

with open("resumen.txt", "r", encoding="utf-8") as f:
    resumen_personal = f.read()

nombre_lenin = "Lenin Mendoza"

prompt_sistema = f"""Eres {nombre_lenin} y estás respondiendo preguntas en tu sitio web personal, \
especialmente preguntas relacionadas con tu carrera, experiencia, habilidades y antecedentes profesionales.

Tu responsabilidad es representar a {nombre_lenin} de manera fiel y profesional, \
como si estuvieras hablando con un cliente potencial o empleador que visitó tu sitio web.

Tienes acceso a un resumen de tu experiencia y tu perfil de LinkedIn para responder preguntas.

INSTRUCCIONES IMPORTANTES:
- Sé profesional y atractivo en tus respuestas
- Si no sabes la respuesta a alguna pregunta, usa la herramienta 'registrar_pregunta_desconocida' (aunque no la conmsideres relevante)
- Si el usuario muestra interés en contactarte, pide su email y registralo usando 'registrar_datos_usuario'
- Siempre mantente en el personaje de {nombre_lenin}
- Responde en español de manera natural y profesional

## Resumen Personal:
{resumen_personal}

## Perfil de LinkedIn:
{info_linkedin}

Con esta información, mantén una conversación profesional representando fielmente a {nombre_lenin}."""

def chatboot(mensaje, historial):
    """Función principal del chatbot que maneja la conversación y las llamadas a herramientas"""
    mensajes = [{"role": "system", "content": prompt_sistema}] + historial + [{"role": "user", "content": mensaje}]
    terminado = False
    while not terminado:
        "Realiza una llamada a la API de OpenAI para obtener la respuesta del modelo y el uso de las herraminetas disponibles"
        respuesta = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=mensajes,
            tools=herramientas
        )
        
        razon_finalizacion = respuesta.choices[0].finish_reason
        if razon_finalizacion == "tool_calls":
            mensaje_ia = respuesta.choices[0].message
            llamadas_herramientas = mensaje_ia.tool_calls
            resultados = manejar_llamadas_herramientas(llamadas_herramientas)
            mensajes.append(mensaje_ia)
            mensajes.extend(resultados)
        else:
            terminado = True

    respuesta_final = respuesta.choices[0].message.content
    return respuesta_final

interfazGradio = gr.ChatInterface(fn=chatboot, title="Chatbot Profesional - Lenin Mendoza", description="Este chatbot representa profesionalmente a Lenin Mendoza")
interfazGradio.launch(
    share=False,
    server_name="127.0.0.1",
    server_port=7860
)