"""La cascada salta EN EL SERVIDOR al tachar, y los botones llevan su dibujo.

Hasta ahora la cascada la lanzaba la pantalla, y si ese aviso fallaba, no pasaba
nada. Ahora la lanza el servidor: da igual quién tache ni desde dónde.
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


cambia_srv("""      if (cuerpo.que) e.que = String(cuerpo.que).slice(0, 60);""",
           """      if (cuerpo.que) e.que = String(cuerpo.que).slice(0, 60);

      /* LA CASCADA, AQUÍ MISMO: la lanza el servidor, no la pantalla.
         Así da igual quién la tache y desde dónde. */
      if (e.hecho) {
        const claveCasc = String(e.t || '')
          .toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
          .replace(/\\s+/g, ' ').trim().slice(0, 120);
        const hijos = (estado.cascadas && estado.cascadas[claveCasc]) || [];
        const hoyC = hoyISO(zona);
        for (const h of hijos) {
          const clave = 'cascada:' + claveCasc + ':' +
            String(h.que || '').toLowerCase().trim() + ':' + hoyC;
          if ((estado.encargos || []).some(x => x.clave === clave && !x.hecho)) continue;
          estado.encargos.push({
            id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
            t: String(h.que || '').slice(0, 300),
            p: ['tienda', 'coordinacion', 'gerencia'].includes(h.p) ? h.p : 'tienda',
            f: hoyC, turno: h.turno || null, diario: false, tipo: 'extra',
            clave: clave, deCascada: claveCasc, q: marca, h: hora, hecho: false
          });
        }
      }""",
           "la cascada salta en el servidor")

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


# los botones del grupo, con su dibujo
cambia("""  tienda: [
    ["calendario", "Calendario"],
    ["panes", "Registro de panes"],
    ["extra", "Tareas extra"],
    ["manana", "Mañana"],
    ["tarde", "Tarde"],
    ["cierre", "Cierre"]
  ],
  coordinacion: [
    ["calendario", "Calendario"],
    ["panes", "Registro de panes"],
    ["extra", "Tareas extra"],
    ["apertura", "Apertura"],
    ["dia", "El día"],
    ["cierre", "Cierre"]
  ]""",
       """  tienda: [
    ["calendario", "Calendario", "📅"],
    ["panes", "Registro de panes", "🍞"],
    ["extra", "Tareas extra", "📌"],
    ["manana", "Mañana", "☀️"],
    ["tarde", "Tarde", "🌤"],
    ["cierre", "Cierre", "🌙"]
  ],
  coordinacion: [
    ["calendario", "Calendario", "📅"],
    ["panes", "Registro de panes", "🍞"],
    ["extra", "Tareas extra", "📌"],
    ["apertura", "Apertura", "🔑"],
    ["dia", "El día", "📋"],
    ["cierre", "Cierre", "🌙"]
  ]""",
       "los botones del grupo con su dibujo")

cambia("""  lista.forEach(([k, n])=>{
    const cuantas = k === "extra" ? extrasPendientes() : 0;
    html += `<button class="menu-btn${cuantas ? " con-pendientes" : ""}" ` +
      `type="button" onclick="abrirSeccion('${k}')">` +
      `<b>${n}</b>` +""",
       """  lista.forEach(([k, n, dibujo])=>{
    const cuantas = k === "extra" ? extrasPendientes() : 0;
    html += `<button class="menu-btn${cuantas ? " con-pendientes" : ""}" ` +
      `type="button" onclick="abrirSeccion('${k}')">` +
      `<span class="menu-dibujo">${dibujo || ""}</span>` +
      `<b>${n}</b>` +""",
       "el dibujo se pinta")

# los del calendario, con su dibujo
cambia("""    [["encargos", "Encargos"], ["llamadas", "Llamadas"], ["tareas", "Tareas"]]
      .map(([k, n]) => `<button class="menu-btn${calBloque === k ? " activo" : ""}" ` +
        `type="button" onclick="abrirCal('${k}')"><b>${n}</b></button>`).join("") +""",
       """    [["encargos", "Encargos", "📦"], ["llamadas", "Llamadas", "📞"], ["tareas", "Tareas", "✏️"]]
      .map(([k, n, d]) => `<button class="menu-btn${calBloque === k ? " activo" : ""}" ` +
        `type="button" onclick="abrirCal('${k}')">` +
        `<span class="menu-dibujo">${d}</span><b>${n}</b></button>`).join("") +""",
       "los del calendario con su dibujo")

# el botón de llamar: un teléfono grande con la palabra debajo
cambia("""`<div class="extra-pasar"><a class="btn-llamar" href="tel:${e.tel}" ` +
          `onclick="marcarLlamada('${e.id}')">Llamar</a>` +""",
       """`<div class="extra-pasar"><a class="btn-llamar" href="tel:${e.tel}" ` +
          `onclick="marcarLlamada('${e.id}')">📞<small>Llamar</small></a>` +""",
       "el botón de llamar, con teléfono")

# el estilo
cambia("  .btn-llamar{display:inline-block; padding:6px 14px; border-radius:9px;\n"
       "              background:var(--verde-oscuro); color:#fff; font-size:12px;\n"
       "              font-weight:800; text-decoration:none}",
       """  .btn-llamar{display:inline-flex; flex-direction:column; align-items:center;
              justify-content:center; min-width:54px; padding:5px 10px; border-radius:11px;
              background:var(--verde-oscuro); color:#fff; font-size:19px;
              line-height:1.05; text-decoration:none}
  .btn-llamar small{font-size:9.5px; font-weight:800; letter-spacing:.03em; margin-top:1px}
  .menu-dibujo{font-size:22px; line-height:1; margin-bottom:5px}""",
       "el estilo del teléfono y del dibujo")

cambia("v-2026-10-26-58", "v-2026-10-26-59", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
