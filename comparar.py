#!/usr/bin/env python3
"""CLI: Ollama extrae las dos GPUs del mensaje y Python las compara."""
import json, sys, urllib.request
from core import DB, NOMBRES, buscar, comparar

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


def main():
    if "--lista" in sys.argv:
        for g in DB:
            print(f"{g['marca']:7}{g['nombre']:16}{g['fps_promedio']:>4} FPS  {g['vram_gb']:>2} GB  {g['precio_usd']:>5} USD")
        return
    print("Comparador de GPUs (Ctrl+C para salir). Disponibles:\n  " + ", ".join(NOMBRES))
    while True:
        try:
            texto = sys.argv[1] if len(sys.argv) > 1 else input("\n> ")
        except (KeyboardInterrupt, EOFError):
            break
        try:
            p = extraer_gpus(texto)
        except Exception as e:
            print(f"Error con Ollama ({e}). Esta corriendo `ollama serve`?")
        else:
            a, sa = buscar(p.get("gpu_1", ""))
            b, sb = buscar(p.get("gpu_2", ""))
            for nom, g, s in ((p.get("gpu_1"), a, sa), (p.get("gpu_2"), b, sb)):
                if not g:
                    print(f"No tengo '{nom}' en la base. Quisiste decir: {', '.join(s)}?")
            if a and b:
                imprimir(comparar(a, b))
        if len(sys.argv) > 1:
            break


if __name__ == "__main__":
    main()
