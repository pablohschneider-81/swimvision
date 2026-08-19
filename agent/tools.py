# agent/tools.py — Herramientas del agente F4F Assistant
# Generado por AgentKit

"""
Herramientas específicas de Fittest4Fit.
Estas funciones extienden las capacidades del agente más allá de responder texto.

NOTA: agent/brain.py todavía es puramente conversacional (system prompt +
historial, sin tool-calling). Estas funciones quedan listas para usarse
desde agent/main.py o desde un flujo de tool-use de la API de Claude más
adelante — no se invocan automáticamente en cada mensaje.
"""

import os
import yaml
import logging

from agent.memory import guardar_lead, guardar_solicitud_mentoria

logger = logging.getLogger("agentkit")


def cargar_info_negocio() -> dict:
    """Carga la información del negocio desde business.yaml."""
    try:
        with open("config/business.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config/business.yaml no encontrado")
        return {}


def obtener_horario() -> dict:
    """Retorna el horario de atención del negocio."""
    info = cargar_info_negocio()
    return {
        "horario": info.get("negocio", {}).get("horario", "No disponible"),
        "esta_abierto": True,  # TODO: calcular según hora actual y horario
    }


def buscar_en_knowledge(consulta: str) -> str:
    """
    Busca información relevante en los archivos de /knowledge.
    Retorna el contenido más relevante encontrado.
    """
    resultados = []
    knowledge_dir = "knowledge"

    if not os.path.exists(knowledge_dir):
        return "No hay archivos de conocimiento disponibles."

    for archivo in os.listdir(knowledge_dir):
        ruta = os.path.join(knowledge_dir, archivo)
        if archivo.startswith(".") or not os.path.isfile(ruta):
            continue
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
                # Búsqueda simple por coincidencia de texto
                if consulta.lower() in contenido.lower():
                    resultados.append(f"[{archivo}]: {contenido[:500]}")
        except (UnicodeDecodeError, IOError):
            continue

    if resultados:
        return "\n---\n".join(resultados)
    return "No encontré información específica sobre eso en mis archivos."


# ════════════════════════════════════════════════════════════
# Calificación de leads y ventas
# ════════════════════════════════════════════════════════════

async def registrar_lead(telefono: str, nombre: str | None, interes: str | None):
    """
    Registra un lead calificado (alguien que mostró interés real en un
    programa) para que Hernán pueda hacer seguimiento comercial.
    """
    await guardar_lead(telefono, nombre, interes)
    logger.info(f"Lead registrado: {telefono} — interés: {interes}")


def calificar_lead(mensaje: str) -> str:
    """
    Heurística simple para calificar el nivel de interés de un mensaje.
    Retorna: "alto", "medio" o "bajo".
    Esto es un punto de partida — Hernán puede reemplazarlo por lógica
    más sofisticada (o un segundo llamado a Claude) según necesite.
    """
    texto = mensaje.lower()
    señales_alto = ["quiero anotarme", "cómo pago", "como pago", "quiero empezar", "quiero comprar", "me interesa"]
    señales_medio = ["cuánto cuesta", "cuanto cuesta", "precio", "info", "información", "informacion"]

    if any(s in texto for s in señales_alto):
        return "alto"
    if any(s in texto for s in señales_medio):
        return "medio"
    return "bajo"


# ════════════════════════════════════════════════════════════
# Agendar mentorías / consultas con Hernán
# ════════════════════════════════════════════════════════════

async def solicitar_mentoria(
    telefono: str, nombre: str | None, disponibilidad: str | None, motivo: str | None
) -> int:
    """
    Registra una solicitud de mentoría/consulta. Hernán no tiene todavía
    un calendario conectado al agente, así que esto queda como una cola de
    solicitudes pendientes que él confirma manualmente (por ejemplo
    revisando `listar_solicitudes_pendientes()` en agent/memory.py).

    Retorna el id de la solicitud creada.
    """
    solicitud_id = await guardar_solicitud_mentoria(telefono, nombre, disponibilidad, motivo)
    logger.info(f"Solicitud de mentoría #{solicitud_id} registrada para {telefono}")
    return solicitud_id
