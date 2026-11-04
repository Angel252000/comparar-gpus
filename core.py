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


def fps_por_100(g):
    """Valor: cuantos FPS se obtienen por cada $100 del precio de salida."""
    return g["fps_promedio"] / g["precio_usd"] * 100


def comparar(a, b):
    """Compara dos GPUs y devuelve un dict con filas y ganadores."""
    filas = [
        ("Rendimiento", a["rendimiento"], b["rendimiento"], ""),
        ("FPS promedio", a["fps_promedio"], b["fps_promedio"], ""),
        ("VRAM", a["vram_gb"], b["vram_gb"], " GB"),
        ("TDP", a["tdp_w"], b["tdp_w"], " W"),
        ("Precio", a["precio_usd"], b["precio_usd"], " USD"),
        ("FPS/$100", round(fps_por_100(a), 1), round(fps_por_100(b), 1), ""),
    ]
    mejor = lambda f1, f2: a["nombre"] if f1 > f2 else b["nombre"] if f2 > f1 else "empate"
    ganadores = {
        "mas_rapida": mejor(a["fps_promedio"], b["fps_promedio"]),
        "mejor_valor": mejor(fps_por_100(a), fps_por_100(b)),
        "mas_eficiente": mejor(a["fps_promedio"] / a["tdp_w"], b["fps_promedio"] / b["tdp_w"]),
    }
    return {"gpu_1": a["nombre"], "gpu_2": b["nombre"], "ganadores": ganadores,
            "filas": [{"metrica": m, "v1": x, "v2": y, "unidad": u} for m, x, y, u in filas]}


def extraer_local(texto):
    """Sin modelo: detecta nombres de la base dentro del texto (para Vercel, donde no hay Ollama)."""
    t = " " + texto.lower() + " "
    hallados = []
    for n in sorted(NOMBRES, key=len, reverse=True):  # los largos primero: 'RTX 5070 Ti' antes que 'RTX 5070'
        i = t.find(" " + n.lower() + " ")
        if i == -1:
            i = t.find(" " + n.lower().split(" ", 1)[-1] + " ") if False else -1
        if i != -1:
            hallados.append((i, n))
            t = t[:i] + " " * (len(n) + 2) + t[i + len(n) + 2:]
    hallados.sort()
    return [n for _, n in hallados]
