"""El desplegable de llamar, por letras: primero la letra, luego los contactos."""
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


cambia("let llamProv = \"\", llamCont = \"\", llamMotivo = \"\", llamTipo = \"extra\";",
       "let llamProv = \"\", llamCont = \"\", llamMotivo = \"\", llamTipo = \"extra\";\n"
       "let llamLetra = \"\";   /* la letra elegida, para no ver los 31 de golpe */",
       "la letra elegida")

cambia("""/* todos los contactos, uno a uno, para el desplegable */
function contactosTodos(){
  const salida = [];
  (proveedores || []).forEach((pv, i)=>{
    (pv.cs || []).forEach((c, j)=>{
      salida.push({ i: i, j: j, prov: pv, c: c });
    });
  });
  return salida;
}""",
       """/* la primera letra del nombre, sin tildes y en mayúscula */
function letraDe(nombre){
  const n = String(nombre || "").normalize("NFD").replace(/[\\u0300-\\u036f]/g, "");
  return (n.trim().charAt(0) || "#").toUpperCase();
}

/* las letras que de verdad tienen proveedores, en orden */
function letrasDisponibles(){
  const vistas = [];
  (proveedores || []).forEach(pv=>{
    const l = letraDe(pv.n);
    if(!vistas.includes(l)) vistas.push(l);
  });
  return vistas.sort();
}

/* todos los contactos (los de una letra, si se ha elegido letra) */
function contactosTodos(){
  const salida = [];
  (proveedores || []).forEach((pv, i)=>{
    if(llamLetra && letraDe(pv.n) !== llamLetra) return;
    (pv.cs || []).forEach((c, j)=>{
      salida.push({ i: i, j: j, prov: pv, c: c });
    });
  });
  return salida;
}

function elegirLetra(v){
  llamLetra = v;
  llamProv = ""; llamCont = "";
  pinta();
}""",
       "las letras disponibles")

cambia("""function bloqueLlamada(){
  const lista = contactosTodos();
  if(!lista.length) return "";
  const opciones = lista.map(x =>
    `<option value="${x.i}-${x.j}"${(String(x.i) === String(llamProv) && String(x.j) === String(llamCont)) ? " selected" : ""}>` +
    `${x.prov.n} · ${x.c.p} · ${telBonito(x.c.t)}</option>`).join("");
  return `<h2 class="bloque">Llamar a un proveedor` +
    `<small>una llamada es una tarea más</small></h2>` +
    `<div class="lista">` +
    `<div class="nueva-nota"><select id="ll-prov" onchange="elegirContacto(this.value)" ` +
    `style="flex:1 1 100%">${opciones}</select></div>` +""",
       """function bloqueLlamada(){
  if(!(proveedores || []).length) return "";
  const letras = letrasDisponibles();
  const opcLetras = `<option value="">— elige la letra —</option>` +
    letras.map(l => `<option value="${l}"${l === llamLetra ? " selected" : ""}>${l}</option>`).join("");
  const lista = contactosTodos();
  const opciones = lista.map(x =>
    `<option value="${x.i}-${x.j}"${(String(x.i) === String(llamProv) && String(x.j) === String(llamCont)) ? " selected" : ""}>` +
    `${x.prov.n} · ${x.c.p} · ${telBonito(x.c.t)}</option>`).join("");
  return `<h2 class="bloque">Llamar a un proveedor` +
    `<small>una llamada es una tarea más</small></h2>` +
    `<div class="lista">` +
    `<div class="nueva-nota">` +
    `<select id="ll-letra" onchange="elegirLetra(this.value)">${opcLetras}</select>` +
    (llamLetra
      ? `<select id="ll-prov" onchange="elegirContacto(this.value)" style="flex:1 1 100%">` +
        `<option value="">— elige el contacto —</option>${opciones}</select>`
      : `<span class="pista">Elige la letra y saldrán sus contactos</span>`) +
    `</div>` +""",
       "el desplegable por letras")

cambia("v-2026-10-26-50", "v-2026-10-26-51", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
