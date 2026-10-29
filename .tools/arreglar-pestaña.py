"""El primer botón de tienda y coordinación es TURNO, no «El día».

El cambio de «General» a «El día» era solo para la Jefa. En tienda y
coordinación ese botón enseña los turnos, así que se llama «Turno».
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


cambia('["general","El día"],["manana","Mañana"]',
       '["general","Turno"],["manana","Mañana"]',
       "tienda: el primero es Turno")

cambia('["general","El día"],["apertura","Apertura"]',
       '["general","Turno"],["apertura","Apertura"]',
       "coordinación: el primero es Turno")

cambia("v-2026-10-26-39", "v-2026-10-26-40", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
