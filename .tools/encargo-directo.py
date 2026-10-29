"""El formulario del encargo lleva sus órdenes dentro: no depende de enganches."""
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


# el botón de abrir
cambia('<button id="enc-nueva" class="btn-add-2" type="button">+ Añadir un encargo</button>',
       '<button id="enc-nueva" class="btn-add-2" type="button"\n'
       '                onclick="formEncargo=true; pinta();">+ Añadir un encargo</button>',
       "abrir el formulario")

# los campos
cambia('id="enc-que" maxlength="200" placeholder="Qué es (1 txapata, 25 pollos…)"\n'
       '             value="${encQue}"',
       'id="enc-que" maxlength="200" placeholder="Qué es (1 txapata, 25 pollos…)"\n'
       '             oninput="encQue=this.value" value="${encQue}"',
       "el qué")

cambia('id="enc-cli" maxlength="60" placeholder="Para quién"\n'
       '             value="${encCliente}"',
       'id="enc-cli" maxlength="60" placeholder="Para quién"\n'
       '             oninput="encCliente=this.value" value="${encCliente}"',
       "el cliente")

cambia('<select id="enc-tipo">',
       '<select id="enc-tipo" onchange="encTipo=this.value; pinta();">',
       "el tipo")

cambia('<input type="date" id="enc-desde" value="${d}">',
       '<input type="date" id="enc-desde" onchange="encDesde=this.value" value="${d}">',
       "el desde")

cambia('<input type="date" id="enc-hasta" value="${encHasta || d}">',
       '<input type="date" id="enc-hasta" onchange="encHasta=this.value" value="${encHasta || d}">',
       "el hasta")

cambia('<select id="enc-antes">', '<select id="enc-antes" onchange="encAntes=this.value">',
       "el ¿hay que pedirlo?")
cambia('<select id="enc-pide">', '<select id="enc-pide" onchange="encPide=this.value">',
       "el quién lo pide")

# los días de la semana
cambia("""        `<button class="dia-btn enc-dia${encDias.includes(i) ? " hoy" : ""}" type="button"
                 data-encdia="${i}">${n}</button>`).join("") + `</div>`;""",
       """        `<button class="dia-btn enc-dia${encDias.includes(i) ? " hoy" : ""}" type="button"
                 onclick="alternarDiaEnc(${i})">${n}</button>`).join("") + `</div>`;""",
       "los días de la semana")

# la función que enciende y apaga un día
cambia("async function guardarEncargo(){",
       """function alternarDiaEnc(i){
  encDias = encDias.includes(i) ? encDias.filter(x => x !== i) : encDias.concat([i]);
  pinta();
}

async function guardarEncargo(){""",
       "alternar un día")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
