"""La prueba de ofertas crea su propia oferta y la borra al terminar."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/probar-ofertas-en-bloque.mjs"
t = open(p, encoding="utf-8").read()

viejo = "const salida = listaOfertas();"
nuevo = """/* la prueba crea su propia oferta: no depende de que haya datos */
const CLAVE = 'ofertas:2026-11-16:prep';
await fetch(U + '/api/encargo', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ quien: 'ge1', t: 'PRUEBA OFERTA · del 16/11 al 30/11',
    p: 'gerencia', f: '2026-10-26', clave: CLAVE })
});
const estado2 = await (await fetch(U + '/api/estado')).json();
const entorno2 = entorno.replace(
  'const encargos = ' + JSON.stringify(estado.encargos || []),
  'const encargos = ' + JSON.stringify(estado2.encargos || []));
const salida = new Function(entorno2 + sacar('listaOfertas') +
  '\\nreturn listaOfertas;')()();"""

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)

# y se borra al terminar
viejo2 = "console.log(`\\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);"
nuevo2 = """/* limpieza */
for (const x of ((await (await fetch(U + '/api/estado')).json()).encargos || [])) {
  if (String(x.clave || '') === CLAVE) {
    await fetch(U + '/api/encargo-borrar', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: x.id })
    });
  }
}

console.log(`\\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);"""
t = t.replace(viejo2, nuevo2, 1)

open(p, "w", encoding="utf-8").write(t)
print("  ok  la prueba de ofertas crea y borra la suya")
