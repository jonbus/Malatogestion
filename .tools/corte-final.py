"""El corte, justo antes del return de bloque()."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

VIEJO = '''           <span class="txt"><b>${t.t}</b>${tag}${n}${quienMarco}</span></div>${sub}</div>`;
  });
  return html + "</div>";
}'''
NUEVO = '''           <span class="txt"><b>${t.t}</b>${tag}${n}${quienMarco}</span></div>${sub}</div>`;
  });
  /* si el bloque está cerrado, se corta por la marca: solo queda el título */
  if(cerrado){
    const i = html.indexOf(MARCA);
    if(i >= 0) html = html.slice(0, i);
    return html;
  }
  return html + "</div>";
}'''

if VIEJO not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(VIEJO, NUEVO, 1)
t = t.replace("v-2026-10-26-47", "v-2026-10-26-48")
open(p, "w", encoding="utf-8").write(t)
print("  ok  el corte, justo antes del return")
