"""Zuaza en el servidor: guardar el pan por día, y borrar un día.

Ojo: el estado se guarda ENTERO. Si un worker no conoce `zuaza`, lo borra al
guardar. Por eso hay que añadirlo en los cinco sitios: vacío, leer, podar,
la respuesta del estado y el endpoint.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs\nube\netlify\functions\nucleo.js"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


# 1 · el estado vacío
rep("tahona: {}, encargosFecha: [], cascadas: {}, nombres: [], proveedores: [], plantilla: {} };",
    "tahona: {}, zuaza: {}, encargosFecha: [], cascadas: {}, nombres: [], proveedores: [], plantilla: {} };",
    "el estado vacío")

# 2 · el podado, igual que la tahona
rep("""  const tahona = {};
  for (const f of Object.keys(estado.tahona || {})) {
    if (f >= desdeRec) tahona[f] = estado.tahona[f];
  }""",
    """  const tahona = {};
  for (const f of Object.keys(estado.tahona || {})) {
    if (f >= desdeRec) tahona[f] = estado.tahona[f];
  }
  /* el pan de Zuaza, igual: se guarda para poder cuadrar las facturas */
  const zuaza = {};
  for (const f of Object.keys(estado.zuaza || {})) {
    if (f >= desdeRec) zuaza[f] = estado.zuaza[f];
  }""",
    "el podado")

rep("    tahona: tahona,", "    tahona: tahona,\n    zuaza: zuaza,", "el podado lo devuelve")

# 3 · leer
rep("""      tahona: guardado.tahona && typeof guardado.tahona === 'object'
        ? guardado.tahona : {},""",
    """      tahona: guardado.tahona && typeof guardado.tahona === 'object'
        ? guardado.tahona : {},
      zuaza: guardado.zuaza && typeof guardado.zuaza === 'object'
        ? guardado.zuaza : {},""",
    "leer")

# 4 · la respuesta del estado
rep("        tahona: estado.tahona, encargosFecha: estado.encargosFecha,",
    "        tahona: estado.tahona, zuaza: estado.zuaza,\n        encargosFecha: estado.encargosFecha,",
    "la respuesta del estado")

# 5 · los dos endpoints, justo después de la tahona
rep("""    /* -------- cambiar el texto o la nota de una tarea del guion */""",
    """    /* -------- borrar el pan de Zuaza de un día */
    if (ruta.endsWith('/zuaza-borrar') && metodo === 'POST') {
      const fecha = String((cuerpo && cuerpo.fecha) || '');
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      const estado = await leer();
      if (estado.zuaza && estado.zuaza[fecha]) {
        delete estado.zuaza[fecha];
        const podado = podar(estado, zona);
        await escribir(podado);
        return { status: 200, body: { ok: true, zuaza: podado.zuaza } };
      }
      return { status: 200, body: { ok: true, zuaza: estado.zuaza || {} } };
    }

    /* -------- el pan de Zuaza: PRIMERO la devolución, después la entrada */
    if (ruta.endsWith('/zuaza') && metodo === 'POST') {
      if (!cuerpo) return { status: 400, body: { ok: false, error: 'faltan los datos' } };
      const fecha = String(cuerpo.fecha || '');
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      if (!marca) return { status: 400, body: { ok: false, error: 'falta quién lo apunta' } };
      const cual = cuerpo.cual === 'entrada' ? 'entrada' : 'devolucion';
      const PANES = ['casero', 'barra_casera', 'molde', 'integral',
                     'cereales', 'maiz', 'pasas_nueces', 'txoripan'];
      const v = cuerpo.valores || {};
      const num = (x) => {
        if (x === '' || x === null || x === undefined) return null;
        const n = Number(x);
        return Number.isFinite(n) && n >= 0 ? Math.round(n * 100) / 100 : null;
      };
      const limpio = {};
      for (const pan of PANES) limpio[pan] = num(v[pan]);
      const estado = await leer();
      if (!estado.zuaza) estado.zuaza = {};
      const dia = estado.zuaza[fecha] || {};
      dia[cual] = limpio;
      dia.q = marca; dia.h = hora;
      estado.zuaza[fecha] = dia;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    zuaza: podado.zuaza } };
    }

    /* -------- cambiar el texto o la nota de una tarea del guion */""",
    "los dos endpoints de Zuaza")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
