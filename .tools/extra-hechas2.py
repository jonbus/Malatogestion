"""La hora a la que se hizo una tarea extra."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

i = t.find("function avisoExtras")
j = t.find("function pintaGerencia")
bloque = t[i:j]

viejo = '''      `<span class="pista">si no da tiempo:</span>` +
      `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}" ` +
      `onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)"></div>`;'''
nuevo = '''      (hecho ? "" :
        `<span class="pista">si no da tiempo:</span>` +
        `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}" ` +
        `onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)">`) +
      `</div>`;'''

if viejo in bloque:
    bloque = bloque.replace(viejo, nuevo, 1)
    t = t[:i] + bloque + t[j:]
    t = t.replace("v-2026-10-26-33", "v-2026-10-26-34")
    open(p, "w", encoding="utf-8").write(t)
    print("  ok  la hecha ya no tiene campo de fecha")
else:
    print("  NO ENCONTRADO")
    sys.exit(1)
