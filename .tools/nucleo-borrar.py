"""Endpoints para BORRAR un recuento y un pan, sin dejar ceros."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs/nube/netlify/functions/nucleo.js"
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


cambia("    /* -------- el pan de la tahona:",
       """    /* -------- borrar un recuento (para las pruebas y para deshacer un error) */
    if (ruta.endsWith('/recuento-borrar') && metodo === 'POST') {
      const fecha = String((cuerpo && cuerpo.fecha) || '');
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      const estado = await leer();
      if (estado.recuentos && estado.recuentos[fecha]) {
        delete estado.recuentos[fecha];
        const podado = podar(estado, zona);
        await escribir(podado);
        return { status: 200, body: { ok: true, recuentos: podado.recuentos } };
      }
      return { status: 200, body: { ok: true, recuentos: estado.recuentos || {} } };
    }

    /* -------- borrar el pan de un día */
    if (ruta.endsWith('/tahona-borrar') && metodo === 'POST') {
      const fecha = String((cuerpo && cuerpo.fecha) || '');
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      const estado = await leer();
      if (estado.tahona && estado.tahona[fecha]) {
        delete estado.tahona[fecha];
        const podado = podar(estado, zona);
        await escribir(podado);
        return { status: 200, body: { ok: true, tahona: podado.tahona } };
      }
      return { status: 200, body: { ok: true, tahona: estado.tahona || {} } };
    }

    /* -------- el pan de la tahona:""",
       "los dos endpoints para borrar")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
