"""Anade la pestana Turnos a la app."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

t = t.replace(
    '["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"],["calendario","Calendario"]]',
    '["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"],["turnos","Turnos"],["calendario","Calendario"]]')
t = t.replace(
    '["apertura","Apertura"],["dia","El día"],["cierre","Cierre"],["calendario","Calendario"]]',
    '["apertura","Apertura"],["dia","El día"],["cierre","Cierre"],["turnos","Turnos"],["calendario","Calendario"]]')
t = t.replace(
    'if(tab === "calendario"){ pintaCalendario(); return; }',
    'if(tab === "turnos"){ pintaTurnos(); return; }\n'
    '  if(tab === "calendario"){ pintaCalendario(); return; }')
t = t.replace(
    "  /* ---- encargar desde el calendario ---- */",
    """  .turno-fila{display:flex; gap:10px; align-items:baseline; padding:11px 14px;
              border-top:1px solid #F2F7F3; flex-wrap:wrap}
  .turno-fila:first-child{border-top:none}
  .turno-fila.libre{color:var(--gris)}
  .turno-fila.es-hoy{background:var(--verde-suave)}
  .t-nombre{flex:0 0 130px; font-weight:600; font-size:13.5px}
  .t-turno{flex:1 1 auto; font-size:12.5px; color:var(--gris)}
  .tag.apagado{background:#EFEFEF; color:var(--gris)}
  /* ---- encargar desde el calendario ---- */""")

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  pestana Turnos anadida")
