"""Pone el corte donde va: al final de bloque(), y lo quita de donde no."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0

# ---------------------------------------------------------------- 1 · quitar el corte mal puesto
MALO = """  });
  if(cerrado){
    const i = html.indexOf(MARCA);
    if(i >= 0) html = html.slice(0, i);
  } else {
    html += `</div>`;
  }
  return html;
}"""
BUENO = """  });
  return html;
}"""
if MALO in t:
    t = t.replace(MALO, BUENO, 1)
    fallos += 1
    print("  ok  quitado el corte de donde no iba")
else:
    print("  NO ENCONTRADO el corte mal puesto")

# ---------------------------------------------------------------- 2 · ponerlo al final de bloque()
VIEJO = """  return html;
}

/* Lo de cada día que se quedó sin hacer y NO tiene destino"""
NUEVO = """  if(cerrado){
    const i = html.indexOf(MARCA);
    if(i >= 0) html = html.slice(0, i);
  } else {
    html += `</div>`;
  }
  return html;
}

/* Lo de cada día que se quedó sin hacer y NO tiene destino"""
if VIEJO in t:
    t = t.replace(VIEJO, NUEVO, 1)
    fallos += 1
    print("  ok  el corte, al final de bloque()")
else:
    print("  NO ENCONTRADO el final de bloque()")

t = t.replace("v-2026-10-26-46", "v-2026-10-26-47")
open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
sys.exit(0 if fallos == 2 else 1)
