"""El pedido de Zuaza: su propia columna, y el mensaje para Patxi.

El pedido NO es la entrada: la entrada es lo que ha llegado hoy; el pedido es
lo que se pide para mañana. Van en columnas distintas.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0

# ============================================================ servidor
p = r"docs\nube\netlify\functions\nucleo.js"
t = open(p, encoding="utf-8").read()


def rep_srv(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO (srv): " + e)


rep_srv("      const cual = cuerpo.cual === 'entrada' ? 'entrada' : 'devolucion';",
        "      const cual = (cuerpo.cual === 'entrada' || cuerpo.cual === 'pedido')\n"
        "        ? cuerpo.cual : 'devolucion';",
        "el servidor acepta el pedido")
open(p, "w", encoding="utf-8").write(t)

# ============================================================ pantalla
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()


def rep(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


# la columna del pedido
rep("""  const dev = dia.devolucion || {};
  const ent = dia.entrada || {};""",
    """  const dev = dia.devolucion || {};
  const ent = dia.entrada || {};
  const ped = dia.pedido || {};""",
    "los tres datos del día")

rep("""        <tr>
          <th style="text-align:left;padding:6px 4px">Pan</th>
          <th style="padding:6px 4px">Devolución</th>
          <th style="padding:6px 4px">Entrada</th>
        </tr>`;""",
    """        <tr>
          <th style="text-align:left;padding:6px 4px">Pan</th>
          <th style="padding:6px 4px">Devolución</th>
          <th style="padding:6px 4px">Entrada</th>
          <th style="padding:6px 4px">Pedido<br><small style="font-weight:400">para mañana</small></th>
        </tr>`;""",
    "la cabecera de la columna")

rep("""        <td style="padding:6px 4px;text-align:center">
          <input type="number" min="0" inputmode="decimal" id="z-e-${k}"
                 value="${v(ent[k])}" style="width:78px;text-align:center"></td>
      </tr>`;""",
    """        <td style="padding:6px 4px;text-align:center">
          <input type="number" min="0" inputmode="decimal" id="z-e-${k}"
                 value="${v(ent[k])}" style="width:78px;text-align:center"></td>
        <td style="padding:6px 4px;text-align:center">
          <input type="number" min="0" inputmode="decimal" id="z-p-${k}"
                 value="${v(ped[k])}" style="width:78px;text-align:center"></td>
      </tr>`;""",
    "la casilla del pedido")

# se guardan los tres
rep("""    for(const par of [["devolucion", "d-"], ["entrada", "e-"]]){""",
    """    for(const par of [["devolucion", "d-"], ["entrada", "e-"], ["pedido", "p-"]]){""",
    "se guardan los tres")

# el botón de WhatsApp, debajo del de guardar
rep("""        <button class="btn-add" type="button" onclick="guardarZuaza()">Guardar el pan de este día</button>
        <span class="pista" style="margin-left:8px">${dia.h ? "apuntado a las " + dia.h : ""}</span>
      </div>""",
    """        <button class="btn-add" type="button" onclick="guardarZuaza()">Guardar el pan de este día</button>
        <span class="pista" style="margin-left:8px">${dia.h ? "apuntado a las " + dia.h : ""}</span>
      </div>
      <div class="nueva-nota" style="border:none;margin-top:6px">
        <button class="btn-add-2" type="button" onclick="mandarPedidoZuaza()">📲 Mandar el pedido a Patxi</button>
        <span class="pista" style="margin-left:8px">abre WhatsApp con el mensaje hecho</span>
      </div>""",
    "el botón de mandar")

# la función del mensaje
rep("function verPan(c){",
    '''/* El mensaje para Patxi. Cantidad primero y descripción después, y sin precios. */
const TELEFONO_ZUAZA = "635 73 99 26";

function textoPedidoZuaza(){
  const dia = (zuaza || {})[fechaSel] || {};
  const ped = dia.pedido || {};
  const lineas = [];
  for(const par of PANES_ZUAZA){
    const k = par[0], n = par[1];
    const c = ped[k];
    if(c === null || c === undefined || c === "") continue;
    if(Number(c) === 0) continue;
    lineas.push(c + " " + n);
  }
  if(!lineas.length) return "";
  const manana = (function(){
    const d = new Date(fechaSel + "T12:00:00");
    d.setDate(d.getDate() + 1);
    return d.toISOString().slice(0, 10);
  })();
  return "Kaixo, tenemos encargado para mañana (" + bonito(manana) + "):\\n\\n" +
    lineas.join("\\n") + "\\n\\nMila esker,\\nMalato";
}

function mandarPedidoZuaza(){
  const texto = textoPedidoZuaza();
  if(!texto){
    ponerSync("error", "No hay nada en la columna del pedido");
    return;
  }
  const numero = TELEFONO_ZUAZA.replace(/\\D/g, "");
  const url = "https://wa.me/" + (numero.length === 9 ? "34" + numero : numero) +
    "?text=" + encodeURIComponent(texto);
  window.open(url, "_blank");
}

function verPan(c){''',
    "la función del mensaje")

rep("v-2026-10-26-79", "v-2026-10-26-80", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
