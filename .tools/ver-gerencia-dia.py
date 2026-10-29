"""Usos de DIA dentro de pintaGerencia."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]
i = js.find("function pintaGerencia")
j = js.find("\nfunction ", i + 10)
cuerpo = js[i:j]
print(f"  pintaGerencia tiene {len(cuerpo)} caracteres")
n = 0
for num, linea in enumerate(cuerpo.split("\n"), 1):
    if "DIA" in linea or "fechaSel" in linea:
        print(f"   {num:>3}: {linea.strip()[:120]}")
        n += 1
print(f"\n  líneas con DIA/fechaSel: {n}")
