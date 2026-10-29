"""La aplicación no mira hacia atrás antes del día en que se empezó de verdad."""
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


# 1 · la fecha en que se empieza de verdad
cambia("const DIAS_ATRAS = ",
       """/* El día en que se empezó a usar de verdad. Antes de esa fecha no se mira
   hacia atrás: lo de antes fueron pruebas y aparecía como «sin hacer». */
const ARRANQUE = "2026-10-26";
const DIAS_ATRAS = """,
       "la fecha de arranque")

# 2 · el bloque «sin hacer» no mira antes del arranque
cambia("""  for(let i = 1; i <= DIAS_ATRAS; i++){
    const f = sumarDias(fechaSel, -i);
    const lista = tabla[semanaDe(f)] || [];""",
       """  for(let i = 1; i <= DIAS_ATRAS; i++){
    const f = sumarDias(fechaSel, -i);
    if(f < ARRANQUE) continue;          // lo de antes del arranque no cuenta
    const lista = tabla[semanaDe(f)] || [];""",
       "«sin hacer» no mira antes del arranque")

if t.count("const ARRANQUE") > 1:
    print("   OJO: ARRANQUE definido dos veces")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
