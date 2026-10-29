"""Busca los accesos con indice [2] y su contexto."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]

print("  === accesos [2] ===")
for m in re.finditer(r"\[2\]", js):
    i = m.start()
    antes = js[max(0, i - 70):i]
    despues = js[i:i + 40]
    print(f"   …{antes}[2]{despues}".replace("\n", " "))
