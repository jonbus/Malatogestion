"""Pone las pruebas a prueba de estado vacío y de la fecha de hoy."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0


def cambia(ruta, viejo, nuevo, etiqueta):
    global fallos
    t = open(ruta, encoding="utf-8").read()
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    open(ruta, "w", encoding="utf-8").write(t.replace(viejo, nuevo))
    print(f"   ok  {etiqueta}")


# ---------------------------------------------------------------- 1 · la prueba de usuario
cambia(".tools/prueba-usuario-completa.mjs",
       "const U = process.env.MALATO_URL || 'https://detect-engineers-chuck-jobs.trycloudflare.com';",
       "const U = process.env.MALATO_URL || 'http://127.0.0.1:8100';",
       "la prueba de usuario apunta al servidor local")

# ---------------------------------------------------------------- 2 · tres perfiles
cambia(".tools/probar-tres-perfiles.mjs",
       "ok('0', 'lleva la versión de hoy', /v-2026-10-23-\\d+/.test(html));",
       "ok('0', 'lleva la versión de hoy', /v-\\d{4}-\\d{2}-\\d{2}-\\d+/.test(html));",
       "la versión vale cualquier día")

cambia(".tools/probar-tres-perfiles.mjs",
       """ok('5', 'Tienda 2 hace mañanas', turnoDe('tienda', 2, HOY).clave === 'A',
  turnoDe('tienda', 2, HOY).clave);
ok('5', 'Tienda 3 hace tardes', turnoDe('tienda', 3, HOY).clave === 'B',
  turnoDe('tienda', 3, HOY).clave);
ok('5', 'Tienda 1 hace el fin de semana', turnoDe('tienda', 1, HOY).clave === 'C',
  turnoDe('tienda', 1, HOY).clave);
ok('5', 'la Coordinadora 2 está de vacaciones', !!ausenciaDe('coordinacion', 2, HOY));
ok('5', 'la Coordinadora 1 trabaja hoy', turnoDe('coordinacion', 1, HOY).trabaja);""",
       """/* se usa una fecha FIJA: los turnos rotan, así que «hoy» cambia la respuesta */
const DIA_FIJO = '2026-10-21';
ok('5', 'Tienda 2 hace mañanas ese día', turnoDe('tienda', 2, DIA_FIJO).clave === 'A',
  turnoDe('tienda', 2, DIA_FIJO).clave);
ok('5', 'Tienda 3 hace tardes ese día', turnoDe('tienda', 3, DIA_FIJO).clave === 'B',
  turnoDe('tienda', 3, DIA_FIJO).clave);
ok('5', 'Tienda 1 hace el fin de semana ese día', turnoDe('tienda', 1, DIA_FIJO).clave === 'C',
  turnoDe('tienda', 1, DIA_FIJO).clave);
ok('5', 'la Coordinadora 2 estaba de vacaciones esos días',
  !!ausenciaDe('coordinacion', 2, '2026-10-21'));
ok('5', 'y ya no lo está el 26', !ausenciaDe('coordinacion', 2, '2026-10-26'));
ok('5', 'la Coordinadora 1 trabaja', turnoDe('coordinacion', 1, DIA_FIJO).trabaja);""",
       "los turnos se prueban con una fecha fija")

print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
