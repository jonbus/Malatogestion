"""Reaplica el lote sobre el generador restaurado (sin la traza, que fue la que rompió)."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = len(t)
fallos = 0


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo)
    print(f"   ok  {etiqueta}")


# ---------------------------------------------------------------- 1 · las fechas
cambia('function semanaDe(f){                     // "2026-10-22" -> "JUE"',
       '/* Una fecha que no vale rompe todo lo que venga detrás: el cálculo del\n'
       '   turno acaba leyendo de undefined y la aplicación se cae. */\n'
       'function fechaBuena(f){\n'
       '  return /^\\d{4}-\\d{2}-\\d{2}$/.test(String(f || "")) ? String(f) : DIA;\n'
       '}\n\n'
       'function semanaDe(f){                     // "2026-10-22" -> "JUE"\n'
       '  f = fechaBuena(f);',
       "fechaBuena + semanaDe protegida")

cambia('function sumarDias(f, n){\n  const [a, m, d] = f.split("-").map(Number);',
       'function sumarDias(f, n){\n  f = fechaBuena(f);\n  const [a, m, d] = f.split("-").map(Number);',
       "sumarDias protegida")

cambia('function bonito(f){\n  const [a, m, d] = f.split("-").map(Number);',
       'function bonito(f){\n  f = fechaBuena(f);\n  const [a, m, d] = f.split("-").map(Number);',
       "bonito protegida")

cambia('function turnoDe(puesto, numero, fecha){\n  const T = DATOS.turnos;\n  const p = fecha.split("-").map(Number);',
       'function turnoDe(puesto, numero, fecha){\n  const T = DATOS.turnos;\n'
       '  fecha = fechaBuena(fecha);\n  const p = fecha.split("-").map(Number);',
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

# ---------------------------------------------------------------- 2 · pestañas de la Jefa
cambia(': [["bandeja","Bandeja"],["general","General"],["calendario","Calendario"]];',
       ': [["general","General"],["turno","Turno"],["calendario","Calendario"]];',
       "pestañas: General · Turno · Calendario")

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
       "destino de cada pestaña")

# ---------------------------------------------------------------- 3 · navegador de fechas
cambia('if(tab === "dia" || (quien.puesto === "tienda" && tab !== "cierre")){',
       'if(tab === "dia" ||\n'
       '     (quien.puesto === "gerencia" && tab === "general") ||\n'
       '     (quien.puesto === "tienda" && tab !== "cierre")){',
       "la Jefa tiene navegador de fechas")

# ---------------------------------------------------------------- 4 · el título, detrás de las fechas
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

# ---------------------------------------------------------------- 5 · lista de ofertas
cambia('  sumar2(DATOS.gerencia.ofertas, "go");',
       '''  sumar2(DATOS.gerencia.ofertas, "go");

  /* las ofertas ya dadas de alta, en orden de fecha. El título lleva dentro
     sus fechas, y pueden convivir varias en las mismas fechas. */
  const misOfertas = (encargos || [])
    .filter(e => !e.hecho && String(e.clave || "").startsWith("ofertas:"))
    .sort((a, b) => String(a.f || "").localeCompare(String(b.f || "")) ||
                    String(a.t || "").localeCompare(String(b.t || "")));
  if(misOfertas.length){
    html += `<h2 class="bloque bloque-viene">Ofertas dadas de alta` +
      `<small>${misOfertas.length} · en orden de fecha</small></h2>` +
      `<div class="lista lista-viene">`;
    misOfertas.forEach(e=>{
      html += `<div class="viene-fila">
          <span class="viene-dia">${bonito(e.f)}</span>
          <span class="viene-que">${e.t}</span>
          <span class="viene-quien">${NOMBRE_PUESTO[e.p] || e.p}</span></div>`;
    });
    html += `</div>`;
  }''',
       "lista de ofertas en orden de fecha")

# ---------------------------------------------------------------- 6 · versión
cambia("v-2026-10-23-26", "v-2026-10-23-27", "versión -27")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  antes {antes} bytes · ahora {len(t)} bytes · fallos {fallos}")
