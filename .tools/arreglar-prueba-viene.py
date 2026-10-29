"""La prueba de «lo que viene» crea sus propios datos."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/probar-viene.mjs"
t = open(p, encoding="utf-8").read()

viejo = "const estado = await (await fetch(U + '/api/estado')).json();"
nuevo = """/* la prueba crea sus propias tareas: no depende de que haya datos */
const CLAVES = ['viene:prueba:coord', 'viene:prueba:jefa'];
for (const c of (await (await fetch(U + '/api/estado')).json()).encargos || []) {
  if (CLAVES.includes(String(c.clave))) {
    await fetch(U + '/api/encargo-borrar', { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: c.id }) });
  }
}
const hoyISO = '2026-10-26';
await fetch(U + '/api/encargo', { method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ quien: 'ge1', t: 'PRUEBA Quitar las vencidas y pegar las nuevas',
    p: 'coordinacion', f: '2026-10-28', clave: CLAVES[0] }) });
await fetch(U + '/api/encargo', { method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ quien: 'ge1', t: 'PRUEBA Pegar la cartelería grande',
    p: 'gerencia', f: '2026-10-28', clave: CLAVES[1] }) });

const estado = await (await fetch(U + '/api/estado')).json();"""

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)

# la fecha de referencia es la de hoy de la prueba, no la del servidor
t = t.replace("const HOY = estado.dia;", "const HOY = hoyISO;", 1)

# las comprobaciones, con los textos de la prueba
t = t.replace("salida.includes('Quitar las vencidas y pegar las nuevas')",
              "salida.includes('PRUEBA Quitar las vencidas')")
t = t.replace("salida.includes('Pegar la cartelería grande')",
              "salida.includes('PRUEBA Pegar la cartelería')")
t = t.replace("salida.includes('26/10')", "salida.includes('28/10')")
t = t.replace("const elMismoDia = bloqueViene('2026-10-26');",
              "const elMismoDia = bloqueViene('2026-10-28');")
t = t.replace("ok('el mismo 26 ya no las anuncia', !elMismoDia.includes('26/10')",
              "ok('el mismo día ya no las anuncia', !elMismoDia.includes('28/10')")

# limpieza
t = t.replace("console.log(`\\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);",
              """/* limpieza */
for (const c of (await (await fetch(U + '/api/estado')).json()).encargos || []) {
  if (CLAVES.includes(String(c.clave))) {
    await fetch(U + '/api/encargo-borrar', { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: c.id }) });
  }
}

console.log(`\\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);""", 1)

open(p, "w", encoding="utf-8").write(t)
print("  ok  la prueba de «lo que viene» crea y borra sus datos")
