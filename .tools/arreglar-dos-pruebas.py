"""Arregla las dos pruebas que quedaron en rojo al limpiar los secretos."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

fallos = 0

# --- 1 · la prueba de cloudflare: llevaba dentro el texto del secreto limpiado
p = r".tools\probar-cloudflare.mjs"
t = open(p, encoding="utf-8").read()
lineas = t.split("\n")
cambiadas = 0
for i, l in enumerate(lineas):
    if "/api/entrar" in l and "pin:" in l and "PIN" not in l:
        lineas[i] = "const buena = await post('/api/entrar', { pin: PIN });"
        cambiadas += 1
    if "la buena entra como gerencia" in l:
        lineas[i] = ("ok('la buena entra como gerencia',\n"
                     "    !PIN || (buena.status === 200 && buena.body.puesto === 'gerencia'),\n"
                     "    PIN ? buena.body : 'sin clave en el entorno: se salta');")
        cambiadas += 1
if cambiadas:
    open(p, "w", encoding="utf-8").write("\n".join(lineas))
    print(f"  ok  la prueba de cloudflare ({cambiadas} lineas)")
    fallos += 1
else:
    print("  NO ENCONTRADO en la prueba de cloudflare")

# --- 2 · la prueba del menú: le falta la función nueva
p2 = r".tools\probar-menu.mjs"
t2 = open(p2, encoding="utf-8").read()
if "panelPlantilla" not in t2:
    t2 = t2.replace("function pintaTabs(){}",
                    'function pintaTabs(){}\nfunction panelPlantilla(){ return ""; }', 1)
    open(p2, "w", encoding="utf-8").write(t2)
    print("  ok  la prueba del menú tiene su stub")
    fallos += 1
else:
    print("  la prueba del menú ya lo tenía")

print(f"\n  cambios: {fallos}")
