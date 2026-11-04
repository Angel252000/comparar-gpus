"""Logica compartida (CLI y API web): base de datos, busqueda y comparacion."""
import difflib, json, pathlib, re, unicodedata

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
    return {"gpu_1": a["nombre"], "gpu_2": b["nombre"], "marca_1": a["marca"], "marca_2": b["marca"],
            "ganadores": ganadores,
            "filas": [{"metrica": m, "v1": x, "v2": y, "unidad": u} for m, x, y, u in filas]}


# ---------- Extraccion tolerante: miles de formas de escribir lo mismo ----------
PREFIJOS = {"rtx", "gtx", "rx", "arc", "radeon", "geforce", "nvidia", "amd", "intel"}
SUFIJOS = {"ti", "xt", "xtx", "super", "s"}


def tokens(texto):
    """'RTX5070Ti', 'rtx-5070 ti', 'Geforce  RTX 5070 TI!' -> ['geforce','rtx','5070','ti']"""
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))       # sin acentos
    t = re.sub(r"(?<=\d)(?=[a-z])|(?<=[a-z])(?=\d)", " ", t)           # 5070ti -> 5070 ti
    toks = re.sub(r"[^a-z0-9]+", " ", t).split()                       # sin signos
    out = []
    for i, k in enumerate(toks):
        if k == "s" and i and toks[i - 1].isdigit():                   # 4070s -> 4070 super
            k = "super"
        elif len(k) >= 4 and difflib.SequenceMatcher(None, k, "super").ratio() >= 0.8:
            k = "super"                                                # suprer, sooper...
        out.append(k)
    return out


def _core(nombre):
    t = tokens(nombre)
    while t and t[0] in PREFIJOS:
        t = t[1:]
    return t


_CORES = sorted(((_core(n), n) for n in NOMBRES), key=lambda x: -len(x[0]))  # los largos primero


def analizar(texto):
    """Devuelve {'encontradas': [nombres en orden], 'desconocidas': [textos que parecen GPU y no estan en la base]}"""
    t = tokens(texto)
    encontradas, desconocidas, i = [], [], 0
    while i < len(t):
        for core, nombre in _CORES:
            if t[i:i + len(core)] == core:
                sig = t[i + len(core)] if i + len(core) < len(t) else ""
                if sig in SUFIJOS:                                       # '5070 super' no existe en la base
                    desconocidas.append(" ".join(t[max(i - 1, 0):i] + core + [sig]).strip())
                elif nombre not in encontradas:
                    encontradas.append(nombre)
                i += len(core)
                break
        else:
            if t[i].isdigit() and len(t[i]) == 4 and i and t[i - 1] in PREFIJOS:
                desconocidas.append(f"{t[i - 1]} {t[i]}")                # 'rtx 3060' no esta en la base
            i += 1
    return {"encontradas": encontradas, "desconocidas": desconocidas}


def extraer_local(texto):
    return analizar(texto)["encontradas"]
