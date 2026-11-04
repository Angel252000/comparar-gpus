"""Funcion serverless de Vercel: GET /api/comparar?q=texto  o  ?gpu1=..&gpu2=.."""
import json, os, sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import NOMBRES, analizar, buscar, comparar


class handler(BaseHTTPRequestHandler):
    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "public, s-maxage=3600")  # la base es fija
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        if "lista" in q:
            return self._json(200, {"gpus": NOMBRES})
        if "q" in q:
            r = analizar(q["q"][0])
            n = r["encontradas"]
            if r["desconocidas"]:
                return self._json(404, {"error": "No tengo en la base: " + ", ".join(r["desconocidas"]) + ".",
                                        "disponibles": NOMBRES})
            if len(n) < 2:
                falta = f"Solo entendi {n[0]}; falta la segunda GPU." if n else "No entendi ninguna GPU."
                return self._json(400, {"error": falta + " Ejemplo: RTX 5070 vs RX 9070 XT.", "disponibles": NOMBRES})
            n1, n2 = n[0], n[1]
        else:
            n1, n2 = q.get("gpu1", [""])[0], q.get("gpu2", [""])[0]
        a, sa = buscar(n1)
        b, sb = buscar(n2)
        if not (a and b):
            return self._json(404, {"error": "GPU no encontrada.", "sugerencias": sa + sb, "disponibles": NOMBRES})
        self._json(200, comparar(a, b))
