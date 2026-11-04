"""Fuera la columna del pedido del registro de panes.

El pedido se hace desde Encargos, no desde el registro del pan.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


# 1 · la cabecera
rep("""          <th style="padding:6px 4px">Pedido<br><small style="font-weight:400">para mañana</small></th>
""", "", "la cabecera del pedido")

# 2 · la casilla
rep("""        <td style="padding:6px 4px;text-align:center">
          <input type="number" min="0" inputmode="decimal" id="z-p-${k}"
                 value="${v(ped[k])}" style="width:78px;text-align:center"></td>
""", "", "la casilla del pedido")

# 3 · el dato y el guardado
rep("  const ped = dia.pedido || {};\n", "", "el dato del pedido")
rep("""    for(const par of [["devolucion", "d-"], ["entrada", "e-"], ["pedido", "p-"]]){""",
    """    for(const par of [["devolucion", "d-"], ["entrada", "e-"]]){""",
    "el guardado")

# 4 · el botón de mandar, y su función
rep("""      <div class="nueva-nota" style="border:none;margin-top:6px">
        <button class="btn-add-2" type="button" onclick="mandarPedidoZuaza()">📲 Mandar el pedido a Patxi</button>
        <span class="pista" style="margin-left:8px">abre WhatsApp con el mensaje hecho</span>
      </div>""", "", "el botón de mandar")

a = t.find("/* El mensaje para Patxi.")
b = t.find("function verPan(c){")
if a > 0 and b > a:
    t = t[:a] + t[b:]
    fallos += 1
    print("  ok  fuera la función del mensaje")
else:
    print("  NO ENCONTRADO la función del mensaje")

rep("v-2026-10-26-83", "v-2026-10-26-84", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
