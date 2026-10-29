"""Los `\\n` del generador tienen que ir dobles para llegar escapados al navegador."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

i = t.find("const MESES_LARGOS")
j = t.find("function descargarPan(){")
if i < 0 or j < 0:
    print("  NO ENCONTRADO el bloque")
    sys.exit(1)
fin = t.find("\n}\n", j)
if fin < 0:
    print("  NO ENCONTRADO el final")
    sys.exit(1)
bloque = t[i:fin + 3]

# ojo: solo los \n que ya están escapados; los saltos de línea de verdad se quedan
arreglado = bloque.replace("\\n", "\\\\n").replace("\\ufeff", "\\\\ufeff")
t = t[:i] + arreglado + t[fin + 3:]
open(p, "w", encoding="utf-8").write(t)
print("  los saltos de línea van escapados")
