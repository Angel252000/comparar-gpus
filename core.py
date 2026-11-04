"""Logica compartida (CLI y API web): base de datos, busqueda y comparacion."""
import difflib, json, pathlib

DB = json.loads((pathlib.Path(__file__).parent / "gpus.json").read_text())
NOMBRES = [g["nombre"] for g in DB]
