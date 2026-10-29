"""Corrige el error de fecha, renombra las pestañas de la Jefa, le pone el
navegador de fechas, mueve el título detrás de las fechas y lista las ofertas."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t


def cambia(viejo, nuevo, etiqueta):
    global t
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        return
    t = t.replace(viejo, nuevo)
    print(f"   ok  {etiqueta}")


# ---------------------------------------------------------------- 1 · las fechas
cambia(
    '''function semanaDe(f){                     // "2026-10-22" -> "JUE"''',
    '''/* Una fecha que no vale rompe todo lo que venga detrás. Antes, una fecha
   vacía hacía que el cálculo del turno leyera de `undefined` y la aplicación
   se cayera con «Cannot read properties of undefined (reading '2')». */
function fechaBuena(f){
  return /^\\d{4}-\\d{2}-\\d{2}$/.test(String(f || "")) ? String(f) : DIA;
}

function semanaDe(f){                     // "2026-10-22" -> "JUE"
  f = fechaBuena(f);''',
    "fechaBuena + semanaDe protegida")

cambia('function sumarDias(f, n){\n  const [a, m, d] = f.split("-").map(Number);',
       'function sumarDias(f, n){\n  f = fechaBuena(f);\n  const [a, m, d] = f.split("-").map(Number);',
       "sumarDias protegida")

cambia('function bonito(f){\n  const [a, m, d] = f.split("-").map(Number);',
       'function bonito(f){\n  f = fechaBuena(f);\n  const [a, m, d] = f.split("-").map(Number);',
       "bonito protegida")

cambia('function turnoDe(puesto, numero, fecha){\n  const T = DATOS.turnos;\n  const p = fecha.split("-").map(Number);',
       'function turnoDe(puesto, numero, fecha){\n  const T = DATOS.turnos;\n  fecha = fechaBuena(fecha);\n  const p = fecha.split("-").map(Number);',
       "turnoDe protegido")

cambia('const tabla = T.coord[semana][numero] || {};',
       'const tabla = ((T.coord[semana] || {})[numero]) || {};',
       "coord a prueba de semana mala")

cambia('const horas = T.oficina[semana][dia] || 0;',
       'const horas = (T.oficina[semana] || {})[dia] || 0;',
       "oficina a prueba de semana mala")

cambia('const t = T.tiendaSemanas[semana][numero];',
       'const t = (T.tiendaSemanas[semana] || {})[numero] || "A";',
       "tienda a prueba de semana mala")

# ---------------------------------------------------------------- 2 · la traza en el cartel
cambia("window.addEventListener(\"unhandledrejection\", e =>\n"
       "  ensenarFallo(\"promesa: \" + (e.reason && e.reason.message || e.reason)));",
       "window.addEventListener(\"unhandledrejection\", e => {\n"
       "  const r = e.reason || {};\n"
       "  const traza = String(r.stack || \"\").split(\"\\n\").slice(1, 3).join(\"  ·  \");\n"
       "  ensenarFallo(\"promesa: \" + (r.message || r) + (traza ? \"   [\" + traza + \"]\" : \"\"));\n"
       "});",
       "el cartel dice también dónde")

# ---------------------------------------------------------------- 3 · pestañas de la Jefa
cambia(': [["bandeja","Bandeja"],["general","General"],["calendario","Calendario"]];',
       ': [["general","General"],["turno","Turno"],["calendario","Calendario"]];',
       "pestañas de la Jefa: General · Turno · Calendario")

cambia('''  if(quien.puesto === "gerencia"){
    if(tab === "general"){ pintaTurnos(); return; }
    if(tab === "calendario"){ pintaCalendario(); return; }
    pintaGerencia(); return;
  }''',
       '''  if(quien.puesto === "gerencia"){
    if(tab === "turno"){ pintaTurnos(); return; }
    if(tab === "calendario"){ pintaCalendario(); return; }
    pintaGerencia(); return;
  }''',
       "el destino de cada pestaña de la Jefa")

# ---------------------------------------------------------------- 4 · navegador de fechas para la Jefa
cambia('if(tab === "dia" || (quien.puesto === "tienda" && tab !== "cierre")){',
       'if(tab === "dia" ||\n'
       '     (quien.puesto === "gerencia" && tab === "general") ||\n'
       '     (quien.puesto === "tienda" && tab !== "cierre")){',
       "la Jefa tiene navegador de fechas")

# ---------------------------------------------------------------- 5 · el título, detrás de las fechas
cambia('''  if(formOfertas){
    html += `<div class="nueva-nota">
        <input type="text" id="of-titulo" maxlength="80"
               placeholder="Título de la oferta (ej.: Vuelta al cole)" value="${ofertasTitulo}">
      </div>
      <div class="nueva-nota">
        <input type="date" id="of-desde" value="${ofertasDesde || lunes}">
        <span class="pista">empiezan</span>
        <input type="date" id="of-hasta" value="${ofertasHasta || ""}">
        <span class="pista">terminan</span>
        <button id="of-add" class="btn-add" type="button">Dar de alta</button>
      </div>`;''',
       '''  if(formOfertas){
    html += `<div class="nueva-nota">
        <input type="date" id="of-desde" value="${ofertasDesde || lunes}">
        <span class="pista">empiezan</span>
        <input type="date" id="of-hasta" value="${ofertasHasta || ""}">
        <span class="pista">terminan</span>
      </div>
      <div class="nueva-nota">
        <input type="text" id="of-titulo" maxlength="80"
               placeholder="Título de la oferta (ej.: Vuelta al cole)" value="${ofertasTitulo}">
        <button id="of-add" class="btn-add" type="button">Dar de alta</button>
      </div>`;''',
       "el título va después de las fechas")

if t == antes:
    print("  SIN CAMBIOS")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  guardado")
