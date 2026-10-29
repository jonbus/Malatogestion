"""De «Oficina» a «Jefa», y una marca de versión para saber qué se está viendo."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------- 1) el nombre
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

t = t.replace('if(s.startsWith("ge")) return "Oficina";', 'if(s.startsWith("ge")) return "Jefa";')
t = t.replace('"hasta": "2026-10-25", "cubre": "Oficina"}', '"hasta": "2026-10-25", "cubre": "Jefa"}')
t = t.replace('{ puesto: "gerencia", numero: 1, nombre: "Oficina" }',
              '{ puesto: "gerencia", numero: 1, nombre: "Jefa" }')
t = t.replace('>Oficina</option>', '>Jefa</option>')
t = t.replace('"gerencia","Gerencia",1', '"gerencia","Jefa",1')
t = t.replace('lo cubre ${aus.cubre}', 'lo cubre la ${aus.cubre}')
t = t.replace('la Oficina', 'la Jefa')
t = t.replace('La Oficina', 'La Jefa')
t = t.replace('de la Oficina', 'de la Jefa')

# ---------------------------------------------------- 2) la marca de versión
t = t.replace(
    '<footer>',
    '<footer><span id="version" style="opacity:.55"></span> · ')

t = t.replace(
    'pintaTurnos(); pinta();',
    'pintaTurnos(); pinta();')

t = t.replace(
    'pintarLogin();\n (async',
    'pintarLogin();\n (async')

# se pinta la marca al arrancar
t = t.replace(
    '/* arranque */',
    '/* arranque */\nconst VERSION = "v-' + '2026-10-23-13";\n')

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  Oficina -> Jefa, y marca de version")
