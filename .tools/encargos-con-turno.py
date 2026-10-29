"""El formulario de encargar tarea: Oficina, turno, y filtrar por turno."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

# --- 1) el bloque filtra por turno
t = t.replace(
    'function bloqueEncargos(puesto, fecha, titulo){\n'
    '  const lista = (encargos || []).filter(e => !e.hecho && e.p === puesto &&\n'
    '    (e.diario || e.f === fecha));',
    'function bloqueEncargos(puesto, fecha, turno, titulo){\n'
    '  const lista = (encargos || []).filter(e => !e.hecho && e.p === puesto &&\n'
    '    (e.diario || e.f === fecha) && (!e.turno || !turno || e.turno === turno));')

# --- 2) las llamadas, con el turno
t = t.replace('bloqueEncargos("gerencia", DIA, "Lo que te han pasado")',
              'bloqueEncargos("gerencia", DIA, null, "Lo que te han pasado")')
t = t.replace('bloqueEncargos("tienda", fechaSel, "Encargos del día")',
              'bloqueEncargos("tienda", fechaSel, tab, "Encargos del día")')
t = t.replace('bloqueEncargos("coordinacion", fechaSel, "Encargos del día")',
              'bloqueEncargos("coordinacion", fechaSel, null, "Encargos del día")')

# --- 3) el formulario: Oficina siempre, y el turno
t = t.replace(
    '    let ops = `<option value="tienda"${puestoTarea==="tienda"?" selected":""}>Tienda</option>` +\n'
    '              `<option value="coordinacion"${puestoTarea==="coordinacion"?" selected":""}>Coordinación</option>`;\n'
    '    if(quien.puesto === "gerencia"){\n'
    '      ops += `<option value="gerencia"${puestoTarea==="gerencia"?" selected":""}>Gerencia</option>`;\n'
    '    }',
    '    const ops = `<option value="tienda"${puestoTarea==="tienda"?" selected":""}>Tienda</option>` +\n'
    '      `<option value="coordinacion"${puestoTarea==="coordinacion"?" selected":""}>Coordinación</option>` +\n'
    '      `<option value="gerencia"${puestoTarea==="gerencia"?" selected":""}>Oficina</option>`;')

t = t.replace(
    '        <select id="tarea-puesto">${ops}</select>\n'
    '        <button id="tarea-add" class="btn-add" type="button">Encargar</button>',
    '        <select id="tarea-puesto">${ops}</select>\n'
    '        <select id="tarea-turno">\n'
    '          <option value=""${turnoTarea===""?" selected":""}>Sin turno</option>\n'
    '          <option value="manana"${turnoTarea==="manana"?" selected":""}>Mañana</option>\n'
    '          <option value="tarde"${turnoTarea==="tarde"?" selected":""}>Tarde</option>\n'
    '        </select>\n'
    '        <button id="tarea-add" class="btn-add" type="button">Encargar</button>')

# --- 4) la globals y el envio
t = t.replace('let formOfertas = false, ofertasDesde = "", ofertasHasta = "";',
              'let formOfertas = false, ofertasDesde = "", ofertasHasta = "";\n'
              'let turnoTarea = "";')

t = t.replace(
    '  await mandarEncargo({ t: t, p: puesto, f: fechaSel });',
    '  await mandarEncargo({ t: t, p: puesto, f: fechaSel, turno: turnoTarea || undefined });')

t = t.replace(
    '  document.getElementById("tarea-puesto") && document.getElementById("tarea-puesto")\n'
    '    .addEventListener("change", e=>{ puestoTarea = e.target.value; });',
    '  document.getElementById("tarea-puesto") && document.getElementById("tarea-puesto")\n'
    '    .addEventListener("change", e=>{ puestoTarea = e.target.value; });\n'
    '  document.getElementById("tarea-turno") && document.getElementById("tarea-turno")\n'
    '    .addEventListener("change", e=>{ turnoTarea = e.target.value; });')

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  formulario con Oficina y turno")
