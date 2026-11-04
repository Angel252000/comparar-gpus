"""Logica compartida (CLI y API web): base de datos, busqueda y comparacion."""
import difflib, json, pathlib

DB = json.loads((pathlib.Path(__file__).parent / "gpus.json").read_text())
NOMBRES = [g["nombre"] for g in DB]


def buscar(nombre):
    """Devuelve (gpu, sugerencias). Si no hay coincidencia, gpu es None."""
    n = nombre.lower()
    for quitar in ("geforce", "radeon", "nvidia", "amd", "intel"):
        n = n.replace(quitar, "")
    n = n.strip()
    norm = {x.lower(): x for x in NOMBRES}
    if n in norm:
        return next(g for g in DB if g["nombre"] == norm[n]), []
    sub = [x for k, x in norm.items() if n and (n in k or k in n)]
    if len(sub) == 1:
        return next(g for g in DB if g["nombre"] == sub[0]), []
    cerca = difflib.get_close_matches(n, list(norm), n=3, cutoff=0.6)
    return None, [norm[c] for c in cerca] or NOMBRES[:5]
