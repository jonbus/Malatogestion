"""La llamada se guarda como llamada (no como extra), con su urgencia aparte.

Y se elige para quién es: antes iba siempre a quien la creaba.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0

# ============================================================ 1 · el servidor
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()


def cambia_srv(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO (srv): {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


cambia_srv("        /* si es una llamada: a qué número y por qué */",
           "        /* una llamada puede ser urgente, sin dejar de ser llamada */\n"
           "        urgente: c.urgente === true,\n"
           "        /* si es una llamada: a qué número y por qué */",
           "el servidor guarda si es urgente")

open(p, "w", encoding="utf-8").write(t)

# ============================================================ 2 · la app
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


# --- el formulario: para quién es
cambia("let llamLetra = \"\";   /* la letra elegida, para no ver los 31 de golpe */",
       "let llamLetra = \"\";   /* la letra elegida, para no ver los 31 de golpe */\n"
       "let llamPara = \"\";    /* para qué puesto es la llamada */",
       "la variable de para quién")

cambia("""    `<select id="ll-tipo" onchange="llamTipo=this.value">` +
    `<option value="extra"${llamTipo === "extra" ? " selected" : ""}>Ordinaria</option>` +
    `<option value="urgente"${llamTipo === "urgente" ? " selected" : ""}>Urgente</option>` +
    `</select>` +
    `<button class="btn-add" type="button" onclick="anadirLlamada()">Añadir la llamada</button>` +
    `</div></div>`;""",
       """    `<select id="ll-tipo" onchange="llamTipo=this.value">` +
    `<option value="extra"${llamTipo === "extra" ? " selected" : ""}>Ordinaria</option>` +
    `<option value="urgente"${llamTipo === "urgente" ? " selected" : ""}>Urgente</option>` +
    `</select>` +
    `</div>` +
    `<div class="nueva-nota">` +
    `<span class="pista">la hace</span>` +
    `<select id="ll-para" onchange="llamPara=this.value">` +
    `<option value="tienda"${(llamPara || quien.puesto) === "tienda" ? " selected" : ""}>Tienda</option>` +
    `<option value="coordinacion"${(llamPara || quien.puesto) === "coordinacion" ? " selected" : ""}>Coordinación</option>` +
    `<option value="gerencia"${(llamPara || quien.puesto) === "gerencia" ? " selected" : ""}>Jefa</option>` +
    `</select>` +
    `<button class="btn-add" type="button" onclick="anadirLlamada()">Añadir la llamada</button>` +
    `</div></div>`;""",
       "el formulario dice para quién es")

# --- y se guarda como llamada
cambia("""  await mandarEncargo({
    t: q.prov.n + " · " + q.c.p,
    p: quien.puesto === "gerencia" ? "gerencia" : quien.puesto,
    f: fechaSel, tipo: valorDe("ll-tipo", llamTipo) || "extra",""",
       """  const urgente = (valorDe("ll-tipo", llamTipo) || "extra") === "urgente";
  await mandarEncargo({
    t: q.prov.n + " · " + q.c.p,
    p: valorDe("ll-para", llamPara) || quien.puesto,
    f: fechaSel,
    tipo: "llamada",          /* SIEMPRE llamada: antes se guardaba como extra */
    urgente: urgente,""",
       "se guarda como llamada, con su urgencia")

# --- la etiqueta de urgente, también en las llamadas
cambia("    const urgente = e.tipo === \"urgente\";\n    const arreglo = e.tipo === \"arreglar\";\n    const etiqueta = urgente ?",
       "    const urgente = e.tipo === \"urgente\" || e.urgente === true;\n"
       "    const arreglo = e.tipo === \"arreglar\";\n    const etiqueta = urgente ?",
       "la llamada urgente lleva su etiqueta")

cambia("v-2026-10-26-55", "v-2026-10-26-56", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
