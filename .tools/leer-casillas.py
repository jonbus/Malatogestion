"""Los formularios leen lo que hay ESCRITO en la casilla, no una variable.

Depender de una variable obliga a que el enganche del campo haya funcionado.
Leyendo la casilla en el momento del clic, no puede fallar.
"""
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


# ---------------------------------------------------------------- tarea extra
cambia("""async function anadirTareaExtra(){
  const t = (textoTarea || "").trim();
  if(!t) return;
  const puesto = puestoTarea;
  const turno = turnoTarea;
  const fecha = fechaSel;""",
       """/* se lee de la casilla en el momento del clic: asi no depende de que
   el enganche del campo haya funcionado */
function valorDe(id, porDefecto){
  const el = document.getElementById(id);
  return el && el.value !== undefined ? el.value : porDefecto;
}

async function anadirTareaExtra(){
  const t = String(valorDe("tarea-txt", textoTarea) || "").trim();
  if(!t){ ponerSync("error", "Escribe qué hay que hacer"); return; }
  const puesto = valorDe("tarea-puesto", puestoTarea) || "tienda";
  const turno = valorDe("tarea-turno", turnoTarea);
  const tipo = valorDe("tarea-tipo", tipoTarea) || "extra";
  const fecha = fechaSel;""",
       "la tarea extra lee la casilla")

cambia("""  await mandarEncargo({ t: t, p: puesto, f: fecha, turno: turno || undefined,
                        tipo: tipoTarea });""",
       """  await mandarEncargo({ t: t, p: puesto, f: fecha, turno: turno || undefined,
                        tipo: tipo });""",
       "manda el tipo leído")

# ---------------------------------------------------------------- encargo
cambia("""async function guardarEncargo(){
  const que = (encQue || "").trim();
  if(!que){ ponerSync("error", "Escribe qué es"); return; }
  const d = encDesde || fechaSel;
  const cuerpo = {
    quien: quien.id, que: que, cliente: encCliente, tipo: encTipo,
    desde: d, hasta: encTipo === "dia" ? d : (encHasta || d),
    dias: encTipo === "semana" ? encDias : [],
    antelacion: Number(encAntes) || 0,
    quienPide: encPide
  };""",
       """async function guardarEncargo(){
  const que = String(valorDe("enc-que", encQue) || "").trim();
  if(!que){ ponerSync("error", "Escribe qué es"); return; }
  const tipo = valorDe("enc-tipo", encTipo) || "dia";
  const d = valorDe("enc-desde", encDesde) || fechaSel;
  const hasta = valorDe("enc-hasta", encHasta) || d;
  const cuerpo = {
    quien: quien.id, que: que,
    cliente: String(valorDe("enc-cli", encCliente) || "").trim(),
    tipo: tipo,
    desde: d, hasta: tipo === "dia" ? d : hasta,
    dias: tipo === "semana" ? encDias : [],
    antelacion: Number(valorDe("enc-antes", encAntes)) || 0,
    quienPide: valorDe("enc-pide", encPide) || "coordinacion"
  };""",
       "el encargo lee las casillas")

# ---------------------------------------------------------------- el pan
cambia("""async function guardarPanDia(dia){
  const ent = {}, dev = {};
  document.querySelectorAll("[data-pane]").forEach(i=>{ ent[i.dataset.pane] = i.value; });
  document.querySelectorAll("[data-pand]").forEach(i=>{ dev[i.dataset.pand] = i.value; });""",
       """async function guardarPanDia(dia){
  const ent = {}, dev = {};
  document.querySelectorAll("[data-pane]").forEach(i=>{ ent[i.dataset.pane] = i.value; });
  document.querySelectorAll("[data-pand]").forEach(i=>{ dev[i.dataset.pand] = i.value; });
  if(!Object.keys(ent).length && !Object.keys(dev).length){
    ponerSync("error", "No hay casillas que guardar");
    return;
  }""",
       "el pan avisa si no hay casillas")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
