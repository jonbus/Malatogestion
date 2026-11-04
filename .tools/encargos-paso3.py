"""Paso 3: el desplegable de verdad, la cantidad y las observaciones.

Y el arreglo del paso 2: al salir de encargos, el formulario se cierra, para
que al volver se entre en el menú de los tres botones y no en donde estabas.
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
        print(f"  OJO, aparece {t.count(v)} veces: " + e)


# ---------------------------------------------------------------- 1 · el formulario se cierra al salir
rep("""function abrirSeccion(k){
  tab = k;
  pintaTabs();""",
    """function abrirSeccion(k){
  tab = k;
  /* al salir de encargos, el formulario se cierra: al volver, los tres botones */
  if(k !== "calendario"){ formEncargo = false; encProveedor = ""; }
  pintaTabs();""",
    "el formulario se cierra al salir de encargos")

# ---------------------------------------------------------------- 2 · los datos nuevos
rep('''/* de quién es el encargo: "zuaza", "tahona", o "" cuando es uno cualquiera */
let encProveedor = "";''',
    '''/* de quién es el encargo: "zuaza", "tahona", o "" cuando es uno cualquiera */
let encProveedor = "";
let encCantidad = "", encNota = "";

/* los productos de cada proveedor, para el desplegable */
function productosDeEncargo(){
  if(encProveedor === "zuaza") return PANES_ZUAZA.map(p => p[1]);
  if(encProveedor === "tahona") return PANES_TAHONA_DOS.map(p => p[1]);
  return [];
}''',
    "los datos y los productos")

# ---------------------------------------------------------------- 3 · el campo: desplegable o texto
rep('''      <span class="pista" style="font-weight:700;flex:1 0 100%">${deQuien}</span>
      <input type="text" id="enc-que" maxlength="200" placeholder="Qué es (1 txapata, 25 pollos…)"
             oninput="encQue=this.value" value="${encQue}">''',
    '''      <span class="pista" style="font-weight:700;flex:1 0 100%">${deQuien}</span>
      ${encProveedor ? `<select id="enc-que" onchange="encQue=this.value">
        <option value="">Elige el producto…</option>
        ${productosDeEncargo().map(n =>
          `<option value="${n}"${encQue === n ? " selected" : ""}>${n}</option>`).join("")}
      </select>
      <input type="number" min="0" inputmode="numeric" id="enc-cant" placeholder="Cantidad"
             oninput="encCantidad=this.value" value="${encCantidad}" style="flex:0 1 110px">`
      : `<input type="text" id="enc-que" maxlength="200" placeholder="Qué es (1 txapata, 25 pollos…)"
             oninput="encQue=this.value" value="${encQue}">`}''',
    "el desplegable y la cantidad")

# las observaciones, solo para los proveedores
rep('''    <div class="nueva-nota">
      <select id="enc-tipo" onchange="encTipo=this.value; pinta();">''',
    '''    ${encProveedor ? `<div class="nueva-nota">
      <input type="text" id="enc-nota" maxlength="300" placeholder="Observaciones (si hace falta algo)"
             oninput="encNota=this.value" value="${encNota}">
    </div>` : ""}
    <div class="nueva-nota">
      <select id="enc-tipo" onchange="encTipo=this.value; pinta();">''',
    "las observaciones")

# ---------------------------------------------------------------- 4 · guardar los tres datos
rep('''    antelacion: Number(valorDe("enc-antes", encAntes)) || 0,
    quienPide: valorDe("enc-pide", encPide) || "coordinacion"
  };''',
    '''    antelacion: Number(valorDe("enc-antes", encAntes)) || 0,
    quienPide: valorDe("enc-pide", encPide) || "coordinacion",
    producto: encProveedor ? que : undefined,
    cantidad: encProveedor ? (Number(valorDe("enc-cant", encCantidad)) || "") : undefined,
    nota: encProveedor ? String(valorDe("enc-nota", encNota) || "").trim() : undefined
  };''',
    "guardar producto, cantidad y nota")

rep('    formEncargo = false; encQue = ""; encCliente = "";',
    '    formEncargo = false; encQue = ""; encCliente = "";\n    encProveedor = ""; encCantidad = ""; encNota = "";',
    "limpiar al guardar")

rep("v-2026-10-26-89", "v-2026-10-26-90", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
