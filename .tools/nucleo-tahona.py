"""Tahona: guardar la entrada del pan y la devolución."""
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


# 1 · el estado vacío y la lectura
cambia("encargos: [], recuentos: {} };", "encargos: [], recuentos: {}, tahona: {} };",
       "estadoVacio con tahona")
cambia("""      recuentos: guardado.recuentos && typeof guardado.recuentos === 'object'
        ? guardado.recuentos : {}""",
       """      recuentos: guardado.recuentos && typeof guardado.recuentos === 'object'
        ? guardado.recuentos : {},
      tahona: guardado.tahona && typeof guardado.tahona === 'object'
        ? guardado.tahona : {}""",
       "leer devuelve tahona")

# 2 · podar
cambia("""  return {
    version: estado.version,
    marcas: marcas,
    recuentos: recuentos,""",
       """  /* el pan de la tahona: se guarda dos años, para poder cotejar facturas */
  const tahona = {};
  for (const f of Object.keys(estado.tahona || {})) {
    if (f >= desdeRec) tahona[f] = estado.tahona[f];
  }
  return {
    version: estado.version,
    marcas: marcas,
    recuentos: recuentos,
    tahona: tahona,""",
       "podar conserva tahona")

# 3 · el estado lo devuelve
cambia("        encargos: estado.encargos, recuentos: estado.recuentos",
       "        encargos: estado.encargos, recuentos: estado.recuentos,\n"
       "        tahona: estado.tahona",
       "el estado devuelve tahona")

# 4 · el endpoint
cambia("    /* -------- mover una tarea extra a otro día",
       """    /* -------- el pan de la tahona: entrada por la mañana, devolución por la noche */
    if (ruta.endsWith('/tahona') && metodo === 'POST') {
      if (!cuerpo) return { status: 400, body: { ok: false, error: 'faltan los datos' } };
      const fecha = String(cuerpo.fecha || '');
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      if (!marca) return { status: 400, body: { ok: false, error: 'falta quién lo apunta' } };
      const num = (x) => {
        if (x === '' || x === null || x === undefined) return null;
        const n = Number(x);
        return Number.isFinite(n) && n >= 0 ? Math.round(n * 100) / 100 : null;
      };
      const estado = await leer();
      if (!estado.tahona) estado.tahona = {};
      const dia = estado.tahona[fecha] || {};
      if (cuerpo.entrada !== undefined) dia.entrada = num(cuerpo.entrada);
      if (cuerpo.devolucion !== undefined) dia.devolucion = num(cuerpo.devolucion);
      dia.q = marca; dia.h = hora;
      estado.tahona[fecha] = dia;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    tahona: podado.tahona } };
    }

    /* -------- mover una tarea extra a otro día""",
       "el endpoint /tahona")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
