"""Las pruebas dejan de escribir en días reales.

El recuento de hoy lo borraba `probar-cloudflare.mjs`: escribía un recuento de
prueba en la fecha de HOY y lo "limpiaba" dejándolo a cero. Eso machacaba el
recuento de verdad. Ahora las pruebas usan una fecha de mentira que no es de
nadie, y borran en vez de poner ceros.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0

# la fecha de mentira: un día que no existe para la tienda
PRUEBA = "2099-01-05"


def cambia(ruta, viejo, nuevo, etiqueta):
    global fallos
    t = open(ruta, encoding="utf-8").read()
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    open(ruta, "w", encoding="utf-8").write(t.replace(viejo, nuevo))
    print(f"   ok  {etiqueta}")


# ---------------------------------------------------------------- 1 · la de Cloudflare
cambia(".tools/probar-cloudflare.mjs",
       "const rec = await post('/api/recuento', {\n  quien: 'co1', fecha: '2026-10-26',",
       f"const rec = await post('/api/recuento', {{\n  quien: 'co1', fecha: '{PRUEBA}',",
       "cloudflare: el recuento va a una fecha de mentira")

cambia(".tools/probar-cloudflare.mjs",
       f"ok('y se lee después', e3.recuentos && e3.recuentos['2026-10-26'], e3.recuentos);",
       f"ok('y se lee después', e3.recuentos && e3.recuentos['{PRUEBA}'], e3.recuentos);",
       "cloudflare: se comprueba en esa fecha")

cambia(".tools/probar-cloudflare.mjs",
       "await post('/api/recuento', { quien: 'co1', fecha: '2026-10-26',\n"
       "  valores: { pollos: '', codillos: '', patatas: '', bravas: '' } });",
       f"/* se borra la clave de la fecha de mentira, sin tocar ningún día real */\n"
       f"await post('/api/recuento-borrar', {{ fecha: '{PRUEBA}' }});",
       "cloudflare: se borra, no se ponen ceros")

# ---------------------------------------------------------------- 2 · la del recuento
t = open(".tools/probar-recuento.mjs", encoding="utf-8").read()
t = t.replace("const LUNES = '2026-10-26';", f"const LUNES = '{PRUEBA}';")
t = t.replace("const JUEVES = '2026-10-29';", "const JUEVES = '2099-01-08';")
t = t.replace("await post('/api/recuento', { quien: 'co1', fecha: LUNES, valores: { pollos: '', codillos: '', patatas: '', bravas: '' } });",
              "await post('/api/recuento-borrar', { fecha: LUNES });")
open(".tools/probar-recuento.mjs", "w", encoding="utf-8").write(t)
print("   ok  la prueba del recuento usa una fecha de mentira")

# ---------------------------------------------------------------- 3 · la de la tahona
t = open(".tools/probar-tahona.mjs", encoding="utf-8").read()
t = t.replace("const HOY = (await (await pedir('/api/estado')).json()).dia;",
              f"/* una fecha que no es de nadie, para no tocar el pan de verdad */\n"
              f"const HOY = '{PRUEBA}';")
t = t.replace("""console.log('\\n   === limpieza ===');
const bruto = await (await pedir('/api/estado')).json();
if (bruto.tahona && bruto.tahona[HOY]) {
  console.log('   (los datos de la tahona se dejan: son de hoy)');
}""",
              """console.log('\\n   === limpieza ===');
await post('/api/tahona-borrar', { fecha: HOY });
console.log('   (borrada la fecha de mentira)');""")
open(".tools/probar-tahona.mjs", "w", encoding="utf-8").write(t)
print("   ok  la prueba de la tahona usa una fecha de mentira")

print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
