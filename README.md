# Comparador de GPUs

Compara dos tarjetas graficas con una base fija (`gpus.json`): rendimiento, FPS, VRAM, TDP, precio y **FPS por cada $100**.
Inspirado en https://www.michaelpcmaster.com/comparar/

## Dos formas de usarlo

| Modo | Como extrae las GPUs del mensaje |
|---|---|
| **CLI** (`comparar.py`) | Un modelo local via Ollama (`gemma3:1b`) con salida JSON tipo function calling |
| **Web** (Vercel) | `core.extraer_local`: busca nombres conocidos en el texto (Vercel no alcanza tu Ollama) |

## Flujo
1. Usuario: "Quiero comparar una RTX 5070 y una RX 9070 XT"
2. Se extraen `gpu_1` y `gpu_2`
3. Python busca ambas en `gpus.json` (exacto, parcial o difuso)
4. Se imprime/dibuja la comparacion y los ganadores

## Uso
```
ollama pull gemma3:1b
python3 comparar.py "RTX 5070 vs RX 9070 XT"   # o sin argumento para modo chat
```
Web local: `vercel dev`.

## Estructura
- `core.py` base, busqueda, comparacion (compartido)
- `comparar.py` CLI con Ollama
- `api/comparar.py` endpoint serverless
- `public/` interfaz web

> Los numeros de `gpus.json` son aproximados; la pagina original carga su tabla con JavaScript y no se pudo extraer automaticamente.
