"""Quita el corte que se coló en bloqueEncargos (no tiene `cerrado`)."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

MALO = ("  });\n"
        "  if(cerrado){\n"
        "    const i = html.indexOf(MARCA);\n"
        "    if(i >= 0) html = html.slice(0, i);\n"
        "  } else {\n"
        "    html += `</div>`;\n"
        "  }\n"
        "  return html;\n"
        "}")

# en bloqueEncargos, el return tiene que ser simple
i = t.find("function bloqueEncargos")
j = t.find("function bloque(titulo", i)
trozo = t[i:j]

if MALO not in trozo:
    print("  NO ENCONTRADO en bloqueEncargos")
    sys.exit(1)

trozo = trozo.replace(MALO, "  });\n  return html;\n}", 1)
t = t[:i] + trozo + t[j:]
open(p, "w", encoding="utf-8").write(t)
print("  ok  quitado el corte de bloqueEncargos")
