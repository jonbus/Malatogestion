"""Arregla: marca de version visible, clave de gerencia en el servidor local,
y las vacaciones en la lista de los siete días."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------- 1) la version, visible
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

t = t.replace(
    "  <main>\n",
    "  <main>\n")
# un pie de verdad, al final del body
t = t.replace(
    "</section>\n\n<script>",
    "</section>\n\n<footer id=\"pie\"><span id=\"version\"></span></footer>\n\n<script>")

# el estilo del pie
t = t.replace(
    "  #logo-login{cursor:pointer}",
    "  #pie{max-width:760px; margin:0 auto; padding:0 16px 40px; font-size:11px;\n"
    "       color:var(--gris); text-align:center}\n"
    "  #logo-login{cursor:pointer}")

# ---------------------------------------------------- 2) las vacaciones en los siete días
t = t.replace(
    "    const quien = GENTE.filter(g => turnoDe(g.puesto, g.numero, f).trabaja)",
    "    const quien = GENTE.filter(g => turnoDe(g.puesto, g.numero, f).trabaja &&\n"
    "                                       !ausenciaDe(g.puesto, g.numero, f))")

if t == antes:
    print("  app: SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  app: pie con version y vacaciones en los siete días")

# ---------------------------------------------------- 3) la clave en el servidor local
p = r"docs/nube/servidor-local.mjs"
t = open(p, encoding="utf-8").read()
antes = t
t = t.replace(
    "const manejar = nucleo.crearManejador({ store });",
    "/* la clave de la jefa: del entorno, o de un fichero al lado */\n"
    "let pinGerencia = process.env.GERENCIA_PIN || '';\n"
    "const F_PIN = path.join(AQUI, '.pin');\n"
    "if (!pinGerencia && fs.existsSync(F_PIN)) {\n"
    "  pinGerencia = fs.readFileSync(F_PIN, 'utf8').trim();\n"
    "}\n"
    "const manejar = nucleo.crearManejador({ store, pinGerencia: pinGerencia });")
if t == antes:
    print("  servidor: SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  servidor local: ya recibe la clave")

# el fichero con la clave
open(r"docs/nube/.pin", "w", encoding="utf-8").write("«la clave de la Jefa — se dice aparte, no se escribe»")
print("  docs/nube/.pin escrito")
