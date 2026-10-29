"""Arregla: el encargo no guardaba sus sub-pasos."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()

viejo = """        opciones: Array.isArray(c.opciones) ? c.opciones.slice(0, 40).map(String) : null,
        que: c.que ? String(c.que).slice(0, 60) : null,"""
nuevo = """        opciones: Array.isArray(c.opciones) ? c.opciones.slice(0, 40).map(String) : null,
        /* los sub-pasos: sin esto, un encargo con pasos los perdía */
        partes: Array.isArray(c.partes) ? c.partes.slice(0, 20).map(String) : null,
        que: c.que ? String(c.que).slice(0, 60) : null,"""

if viejo in t:
    open(p, "w", encoding="utf-8").write(t.replace(viejo, nuevo, 1))
    print("  ok  el encargo guarda sus sub-pasos")
else:
    print("  NO ENCONTRADO")
