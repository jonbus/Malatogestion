"""Las tareas de «SIN HACER» se pueden tachar, en su día de verdad."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

i = t.find("function atenderClic")
if i < 0:
    print("  NO ENCONTRADO atenderClic")
    sys.exit(1)

marca = "const k = it.dataset.k;"
j = t.find(marca, i)
if j < 0:
    print("  NO ENCONTRADO donde se lee la tarea")
    sys.exit(1)

if "ARR[k]" in t[j:j + 400]:
    print("  ya estaba")
    sys.exit(0)

nuevo = (marca + "\n"
         "    /* las de «SIN HACER» se tachan EN SU DÍA, no en el que se está mirando */\n"
         "    if(String(k).indexOf(\"arr\") === 0){\n"
         "      const a = ARR[k];\n"
         "      if(a) tocarEn(a.f, a.k, !hechaEn(a.f, a.k));\n"
         "      return;\n"
         "    }")

t = t[:j] + nuevo + t[j + len(marca):]
t = t.replace("v-2026-10-26-74", "v-2026-10-26-75")
open(p, "w", encoding="utf-8").write(t)
print("  ok  las de SIN HACER se pueden tachar")
