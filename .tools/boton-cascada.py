"""El «＋ cuando se haga, crear…» en cada tarea: las del día y las extra."""
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


# las tareas del día
cambia("""           <span class="txt"><b>${t.t}</b>${tag}${n}${quienMarco}</span></div>${sub}</div>`;""",
       """           <span class="txt"><b>${t.t}</b>${tag}${n}${quienMarco}</span></div>${sub}` +
           lineaCascada(k, t.t) + `</div>`;""",
       "el botón en las tareas del día")

# las tareas extra
cambia("    TXTENC[e.id] = e.t;",
       "    TXTENC[e.id] = e.t;\n    REG[\"e_\" + e.id] = e;",
       "las extra se pueden tocar")

cambia("""      `<span class="caja"></span><span class="extra-txt">` +
      (e.tipo === "llamada" ? "📞 " : "") + `${e.t}</span>${etiqueta}</div>` +""",
       """      `<span class="caja"></span><span class="extra-txt">` +
      (e.tipo === "llamada" ? "📞 " : "") + `${e.t}</span>${etiqueta}</div>` +
      lineaCascada("e_" + e.id, e.t) +""",
       "el botón en las tareas extra")

cambia("v-2026-10-26-62", "v-2026-10-26-63", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
