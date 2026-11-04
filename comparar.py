#!/usr/bin/env python3
"""CLI: Ollama extrae las dos GPUs del mensaje y Python las compara."""
import json, sys, urllib.request
from core import NOMBRES, buscar, comparar

MODEL = "gemma3:1b"
URL = "http://localhost:11434/api/chat"

# Definicion de la "funcion" que el modelo debe llamar
FUNCION = {"name": "comparar_gpus", "parameters": {
    "type": "object",
    "properties": {"gpu_1": {"type": "string"}, "gpu_2": {"type": "string"}},
    "required": ["gpu_1", "gpu_2"]}}


def extraer_gpus(texto):
    prompt = (f"Funcion disponible: {json.dumps(FUNCION)}\n"
              "Extrae los nombres de las dos GPUs que el usuario quiere comparar, "
              "tal como los escribio. Responde SOLO con JSON {\"gpu_1\":...,\"gpu_2\":...}.\n"
              f"Usuario: {texto}")
    body = {"model": MODEL, "stream": False, "format": FUNCION["parameters"],
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    return json.loads(r["message"]["content"])
