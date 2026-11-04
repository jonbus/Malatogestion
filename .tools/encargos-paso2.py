"""Paso 2: los tres botones en el alta de encargos.

Zuaza · Tahona · Varios. Al tocar uno se abre el formulario y queda dicho de
qué es. Todavía no cambia los campos: eso es el paso 3.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if t.count(v) == 1:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    elif t.count(v) == 0:
        print("  NO ENCONTRADO: " + e)
    else:
        print(f"  OJO: aparece {t.count(v)} veces: " + e)


# 1 · el dato de qué proveedor se está pidiendo
rep('''let formEncargo = false, encQue = "", encCliente = "", encTipo = "dia",
    encDesde = "", encHasta = "", encDias = [], encAntes = "1", encPide = "coordinacion";''',
    '''let formEncargo = false, encQue = "", encCliente = "", encTipo = "dia",
    encDesde = "", encHasta = "", encDias = [], encAntes = "1", encPide = "coordinacion";
/* de quién es el encargo: "zuaza", "tahona", o "" cuando es uno cualquiera */
let encProveedor = "";''',
    "el dato del proveedor")

# 2 · los tres botones, cuando el formulario está cerrado
rep('''  if(!formEncargo){
    return html + `<div class="lista"><div class="nueva-nota fila-tarea">
        <button id="enc-nueva" class="btn-add-2" type="button"
                onclick="formEncargo=true; pinta();">+ Añadir un encargo</button>
        <span class="pista">Si hay que pedirlo antes, saldrá un aviso el día de pedirlo</span>
      </div></div>`;
  }''',
    '''  if(!formEncargo){
    return html + `<div class="lista">
      <div class="nueva-nota fila-tarea">
        <button class="btn-add-2" type="button" onclick="abrirEncargoProveedor('zuaza')">Zuaza</button>
        <button class="btn-add-2" type="button" onclick="abrirEncargoProveedor('tahona')">Tahona</button>
        <button class="btn-add-2" type="button" onclick="abrirEncargoProveedor('')">Varios</button>
      </div>
      <div class="nueva-nota fila-tarea">
        <button id="enc-nueva" class="btn-add-2" type="button"
                onclick="abrirEncargoProveedor('')">+ Añadir un encargo</button>
        <span class="pista">Si hay que pedirlo antes, saldrá un aviso el día de pedirlo</span>
      </div></div>`;
  }''',
    "los tres botones")

# 3 · en el formulario, decir de quién es
rep('''  html += `<div class="lista"><div class="nueva-nota">
      <input type="text" id="enc-que" maxlength="200" placeholder="Qué es (1 txapata, 25 pollos…)"''',
    '''  const deQuien = encProveedor === "zuaza" ? "Pedido a Zuaza"
    : encProveedor === "tahona" ? "Pedido a la Tahona"
    : "Encargo";
  html += `<div class="lista"><div class="nueva-nota">
      <span class="pista" style="font-weight:700;flex:1 0 100%">${deQuien}</span>
      <input type="text" id="enc-que" maxlength="200" placeholder="Qué es (1 txapata, 25 pollos…)"''',
    "la etiqueta de quién es")

# 4 · la función que abre el formulario de cada uno
rep("function alternarDiaEnc(i){",
    '''function abrirEncargoProveedor(c){
  encProveedor = (c === "zuaza" || c === "tahona") ? c : "";
  encQue = "";
  formEncargo = true;
  pinta();
}

function alternarDiaEnc(i){''',
    "la función que lo abre")

rep("v-2026-10-26-88", "v-2026-10-26-89", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
