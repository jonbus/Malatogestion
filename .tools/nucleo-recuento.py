"""Añade el recuento del lunes al servidor: guardar, devolver y no perderlo."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()
antes = len(t)
fallos = 0


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


# 1 · el estado vacío ya trae recuentos
cambia("return { version: 0, marcas: {}, fichajes: [], traslados: {}, notas: {}, encargos: [] };",
       "return { version: 0, marcas: {}, fichajes: [], traslados: {}, notas: {},\n"
       "             encargos: [], recuentos: {} };",
       "estadoVacio con recuentos")

# 2 · podar los conserva (los de los últimos 400 días: dos años de lunes)
cambia("""  return {
    version: estado.version,
    marcas: marcas,""",
       """  /* Los recuentos del lunes se guardan mucho más tiempo: son el histórico
     con el que se hacen los pedidos. */
  const limiteRec = new Date();
  limiteRec.setDate(limiteRec.getDate() - 400);
  const desdeRec = limiteRec.toLocaleDateString('en-CA',
    { timeZone: zona || 'Europe/Madrid' });
  const recuentos = {};
  for (const f of Object.keys(estado.recuentos || {})) {
    if (f >= desdeRec) recuentos[f] = estado.recuentos[f];
  }
  return {
    version: estado.version,
    marcas: marcas,
    recuentos: recuentos,""",
       "podar conserva los recuentos")

# 3 · el estado los devuelve
cambia("        notas: estado.notas, fichajes: estado.fichajes,\n        encargos: estado.encargos",
       "        notas: estado.notas, fichajes: estado.fichajes,\n"
       "        encargos: estado.encargos, recuentos: estado.recuentos",
       "el estado devuelve recuentos")

# 4 · el endpoint para guardarlos
cambia("    /* -------- añadir una nota al calendario */",
       """    /* -------- el recuento del lunes: lo que sobró del asador el fin de semana.
       Es el stock inicial antes de hacer los pedidos. */
    if (ruta.endsWith('/recuento') && metodo === 'POST') {
      if (!cuerpo) return { status: 400, body: { ok: false, error: 'faltan los datos' } };
      const fecha = String(cuerpo.fecha || '');
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      if (!marca) return { status: 400, body: { ok: false, error: 'falta quién lo apunta' } };
      const v = cuerpo.valores || {};
      const num = (x) => {
        const n = Number(x);
        return Number.isFinite(n) && n >= 0 ? Math.round(n * 100) / 100 : 0;
      };
      const estado = await leer();
      if (!estado.recuentos) estado.recuentos = {};
      estado.recuentos[fecha] = {
        pollos: num(v.pollos), codillos: num(v.codillos),
        patatas: num(v.patatas), bravas: num(v.bravas),
        q: marca, h: hora
      };
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    recuentos: podado.recuentos } };
    }

    /* -------- añadir una nota al calendario */""",
       "el endpoint /recuento")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  {antes} -> {len(t)} bytes · fallos {fallos}")
