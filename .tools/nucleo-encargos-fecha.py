"""Encargos: lo que hay que tener un día y hay que pedir antes.

Se guarda la SERIE, no cada entrega: las fechas se deducen.
Un dato, no treinta.
"""
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


# 1 · el estado
cambia("encargos: [], recuentos: {}, tahona: {} };",
       "encargos: [], recuentos: {}, tahona: {}, encargosFecha: [] };",
       "estadoVacio con encargosFecha")

cambia("""      tahona: guardado.tahona && typeof guardado.tahona === 'object'
        ? guardado.tahona : {}""",
       """      tahona: guardado.tahona && typeof guardado.tahona === 'object'
        ? guardado.tahona : {},
      encargosFecha: Array.isArray(guardado.encargosFecha) ? guardado.encargosFecha : []""",
       "leer devuelve encargosFecha")

cambia("""    recuentos: recuentos,
    tahona: tahona,""",
       """    recuentos: recuentos,
    tahona: tahona,
    /* los encargos no caducan: se quedan hasta que se reciben */
    encargosFecha: (estado.encargosFecha || []).filter(x => {
      const fin = x.hasta || x.desde || '';
      return fin >= desdeNotas || !x.recibido;
    }),""",
       "podar conserva los encargos")

cambia("        tahona: estado.tahona",
       "        tahona: estado.tahona, encargosFecha: estado.encargosFecha",
       "el estado los devuelve")

# 2 · crear
cambia("    /* -------- el visto bueno de coordinación al recuento del lunes */",
       """    /* -------- encargos: lo que hay que tener un día y hay que pedir antes */
    if (ruta.endsWith('/encargo-fecha') && metodo === 'POST') {
      const c = cuerpo || {};
      const que = String(c.que || '').trim().slice(0, 200);
      if (!que) return { status: 400, body: { ok: false, error: 'falta qué es' } };
      const tipo = ['dia', 'rango', 'semana'].includes(c.tipo) ? c.tipo : 'dia';
      const desde = String(c.desde || '');
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(desde)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      let hasta = String(c.hasta || desde);
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(hasta) || hasta < desde) hasta = desde;
      if (tipo === 'dia') hasta = desde;
      const dias = Array.isArray(c.dias)
        ? c.dias.map(Number).filter(n => n >= 0 && n <= 6) : [];
      if (tipo === 'semana' && !dias.length) {
        return { status: 400, body: { ok: false, error: 'elige al menos un día' } };
      }
      const antelacion = Number.isFinite(Number(c.antelacion))
        ? Math.max(0, Math.min(60, Number(c.antelacion))) : 0;
      const estado = await leer();
      if (!estado.encargosFecha) estado.encargosFecha = [];
      const e = {
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
        que: que,
        cliente: String(c.cliente || '').trim().slice(0, 60),
        tipo: tipo, desde: desde, hasta: hasta, dias: dias,
        antelacion: antelacion,
        quienPide: String(c.quienPide || 'coordinacion').slice(0, 20),
        quienRecibe: String(c.quienRecibe || 'coordinacion').slice(0, 20),
        q: marca, h: hora,
        pedidos: {},      /* por fecha de entrega: true cuando se pidió */
        recibidos: {}     /* por fecha de entrega: true cuando llegó */
      };
      estado.encargosFecha.push(e);
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, version: podado.version,
                                    encargosFecha: podado.encargosFecha } };
    }

    /* -------- marcar un encargo: pedido o recibido, en una fecha de entrega */
    if (ruta.endsWith('/encargo-fecha-hecho') && metodo === 'POST') {
      const c = cuerpo || {};
      const fecha = String(c.fecha || '');
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      const cual = c.cual === 'recibido' ? 'recibidos' : 'pedidos';
      const estado = await leer();
      const e = (estado.encargosFecha || []).find(x => String(x.id) === String(c.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe ese encargo' } };
      if (!e[cual]) e[cual] = {};
      if (c.valor === false) delete e[cual][fecha];
      else e[cual][fecha] = marca || true;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, encargosFecha: podado.encargosFecha } };
    }

    /* -------- borrar un encargo */
    if (ruta.endsWith('/encargo-fecha-borrar') && metodo === 'POST') {
      const estado = await leer();
      const antes = (estado.encargosFecha || []).length;
      estado.encargosFecha = (estado.encargosFecha || [])
        .filter(x => String(x.id) !== String((cuerpo && cuerpo.id) || ''));
      if (estado.encargosFecha.length === antes) {
        return { status: 404, body: { ok: false, error: 'no existe ese encargo' } };
      }
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, encargosFecha: podado.encargosFecha } };
    }

    /* -------- el visto bueno de coordinación al recuento del lunes */""",
       "los tres endpoints de encargos")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
