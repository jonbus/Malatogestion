"""Escapa los saltos de línea del bloque del informe."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

i = t.find("const MESES_LARGOS")
j = t.find("async function guardarTahona(cual){")
if i < 0 or j < 0:
    print("  NO ENCONTRADO")
    sys.exit(1)
bloque = t[i:j]
arreglado = bloque.replace("\\n", "\\\\n").replace("\\ufeff", "\\\\ufeff")
t = t[:i] + arreglado + t[j:]
open(p, "w", encoding="utf-8").write(t)
print("  saltos de línea escapados")
