"""Comprueba que las dos imágenes incrustadas son distintas."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

h = open("docs/nube/public/index.html", encoding="utf-8").read()
ls = re.findall(r'src="data:image/png;base64,([^"]{40})', h)
print(f"  imágenes incrustadas: {len(ls)}")
print(f"  son distintas: {len(set(ls)) == len(ls)}")
for i, x in enumerate(ls):
    print(f"    {i+1}: {x[:30]}…")

por = open("docs/nube/public/index.html", encoding="utf-8").read()
s = por.split("<script>")[1].split("</script>")[0]
open(".tools/_chk.js", "w", encoding="utf-8").write(s)
print("  js extraído")
