"""Muestra el escuchador delegado ya generado."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]
i = js.find("function atenderClic")
print(js[i:i + 1250])
