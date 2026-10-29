"""La bandeja de la Jefa deja de estar atada a hoy: sigue a la fecha elegida."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

# --- la bandeja sigue al día elegido, como tienda y coordinación
t = t.replace(
    'function pintaGerencia(){\n  const W = semanaDe(DIA);',
    'function pintaGerencia(){\n'
    '  /* sigue al día elegido en el calendario, igual que tienda y coordinación */\n'
    '  const W = semanaDe(fechaSel);\n'
    '  const ES_HOY_G = (fechaSel === DIA);')
t = t.replace('<b>${DIAS.find(x=>x[0]===W)[1]} ${bonito(DIA)}</b>',
              '<b>${DIAS.find(x=>x[0]===W)[1]} ${bonito(fechaSel)}</b>')
t = t.replace('Hoy es ${DIAS.find(x=>x[0]===W)[1].toLowerCase()}: la gerencia va de lunes a viernes.',
              'Es ${DIAS.find(x=>x[0]===W)[1].toLowerCase()}: la gerencia va de lunes a viernes.')
t = t.replace('html += bloqueEncargos("gerencia", DIA, null, "Tareas extra");',
              'html += bloqueEncargos("gerencia", fechaSel, null, "Tareas extra");')
t = t.replace('html += bloqueViene(DIA);', 'html += bloqueViene(fechaSel);')

# --- y el subtítulo dice si no es hoy
t = t.replace('document.getElementById("sub").textContent = "Bandeja · elige por dónde empiezas";',
              'document.getElementById("sub").textContent = "Bandeja · " + bonito(fechaSel) +\n'
              '    (ES_HOY_G ? "" : "  (no es hoy)");')

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  la bandeja de la Jefa sigue al día elegido")
