"""Mete el corte antes del return de bloque(), buscándolo por posición."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

i = t.find("function bloque(titulo, tareas, pre, extra){")
if i < 0:
    print("  NO ENCONTRADO bloque()")
    sys.exit(1)

j = t.find('return html + "</div>";', i)
if j < 0:
    print("  NO ENCONTRADO el return")
    sys.exit(1)

# ¿ya está puesto?
if "indexOf(MARCA)" in t[i:j]:
    print("  ya estaba puesto")
    sys.exit(0)

corte = '''/* si el bloque está cerrado, se corta por la marca: solo queda el título */
  if(cerrado){
    const i = html.indexOf(MARCA);
    if(i >= 0) html = html.slice(0, i);
    return html;
  }
  '''
t = t[:j] + corte + t[j:]
t = t.replace("v-2026-10-26-47", "v-2026-10-26-48")
t = t.replace("v-2026-10-26-48", "v-2026-10-26-48")
open(p, "w", encoding="utf-8").write(t)
print("  ok  el corte, antes del return de bloque()")
