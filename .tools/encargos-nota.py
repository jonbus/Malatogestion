"""Las tres respuestas del resumen, y la observación en el servidor.

1 · Varios no lleva cantidad.
2 · El resumen enseña todo, también los días pasados.
3 · La observación se ve en el resumen.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- el documento
p = r"docs\ENCARGOS-PROVEEDOR.md"
t = open(p, encoding="utf-8").read()

viejo = """## 6 · Lo que falta decidir

| | |
|---|---|
| **¿«Varios» necesita también cantidad?** | **o es solo texto libre, como ahora** |
| **¿El resumen enseña los días ya pasados?** | **o solo de hoy en adelante** |
| **¿La observación se ve en el resumen?** | **o solo en el encargo** |"""

nuevo = """## 6 · Lo que ya está decidido

| | |
|---|---|
| **«Varios»** | **NO lleva cantidad** — **es texto libre, como ahora** |
| **El resumen** | **enseña TODO, también los días pasados** — **para poder comprobar cualquier cosa en cualquier momento** |
| **La observación** | **se ve en el resumen** |

> **Y lo de «enseña todo» tiene una consecuencia buena**: **el resumen no es solo para pedir, es también el histórico**. **Si un día alguien pregunta «¿qué pedimos el jueves pasado?», se mira ahí.**"""

t = t.replace(viejo, nuevo, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  el documento, con las tres respuestas")

# ---------------------------------------------------------------- el servidor
p2 = r"docs\nube\netlify\functions\nucleo.js"
t2 = open(p2, encoding="utf-8").read()

ancla = "        cantidad: Number.isFinite(Number(c.cantidad)) ? Number(c.cantidad) : undefined,"
nueva = (ancla + "\n"
         "        /* la observación: texto libre, lo que haga falta escribir */\n"
         "        nota: c.nota ? String(c.nota).slice(0, 300) : undefined,")

if ancla not in t2:
    print("  NO ENCONTRADO el sitio de la cantidad")
    sys.exit(1)

if "nota: c.nota" in t2:
    print("  la observación ya estaba")
else:
    t2 = t2.replace(ancla, nueva, 1)
    open(p2, "w", encoding="utf-8").write(t2)
    print("  ok  el encargo guarda la observación")
