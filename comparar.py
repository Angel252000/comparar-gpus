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


def imprimir(c):
    w = max(len(c["gpu_1"]), len(c["gpu_2"]), 8)
    print(f"\n{'':14}{c['gpu_1']:>{w+2}}{c['gpu_2']:>{w+2}}")
    for f in c["filas"]:
        print(f"{f['metrica']:14}{str(f['v1'])+f['unidad']:>{w+2}}{str(f['v2'])+f['unidad']:>{w+2}}")
    g = c["ganadores"]
    print(f"\nMas rapida: {g['mas_rapida']} | Mejor valor: {g['mejor_valor']} | Mas eficiente: {g['mas_eficiente']}")
