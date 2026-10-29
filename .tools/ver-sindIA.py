"""Qué alimenta los bloques de «SIN HACER» y «Pasadas a este día»."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]

for nombre in ("sinDia", "pasadasA", "pendientes"):
    i = js.find("function " + nombre + "(")
    if i < 0:
        i = js.find(nombre + " =")
    if i < 0:
        print(f"  ({nombre}: no encontrado)")
        continue
    print(f"=== {nombre} ===")
    print(js[i:i + 700])
    print()
