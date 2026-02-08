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

 
