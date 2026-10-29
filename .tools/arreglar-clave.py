"""La variable `clave` tapaba la función `clave` de la aplicación.

Se llama `claveBloqueAhora` y no se parece a nada que ya exista.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


cambia("  const clave = claveBloque(pre, titulo);",
       "  const claveB = claveBloque(pre, titulo);",
       "la variable ya no se llama clave")

cambia("  const cerrado = completo ? true : (PLEGADOS[clave] === undefined ? true : PLEGADOS[clave]);",
       "  const cerrado = completo ? true : (PLEGADOS[claveB] === undefined ? true : PLEGADOS[claveB]);",
       "el estado se lee con el nombre nuevo")

cambia("`onclick=\"plegar('${clave}')\">`",
       "`onclick=\"plegar('${claveB}')\">`",
       "el botón usa el nombre nuevo")

cambia("v-2026-10-26-44", "v-2026-10-26-45", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
