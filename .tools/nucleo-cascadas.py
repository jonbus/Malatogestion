"""Cascadas: guardar la cadena y lanzarla al terminar la tarea.

Una tarea que, al hacerse, hace nacer la siguiente. El hijo NO EXISTE hasta
que el padre se hace. Si ya estaba puesto, no se duplica. Nunca nace en el pasado.
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


# ---------------------------------------------------------------- 1 · el estado
cambia("encargos: [], recuentos: {}, tahona: {}, encargosFecha: [] };",
       "encargos: [], recuentos: {}, tahona: {}, encargosFecha: [], cascadas: {} };",
       "estadoVacio con cascadas")

cambia("""      encargosFecha: Array.isArray(guardado.encargosFecha) ? guardado.encargosFecha : []""",
       """      encargosFecha: Array.isArray(guardado.encargosFecha) ? guardado.encargosFecha : [],
      cascadas: guardado.cascadas && typeof guardado.cascadas === 'object'
        ? guardado.cascadas : {}""",
       "leer devuelve cascadas")

cambia("""    encargosFecha: (estado.encargosFecha || []).filter(x => {""",
       """    cascadas: estado.cascadas || {},
    encargosFecha: (estado.encargosFecha || []).filter(x => {""",
       "podar conserva cascadas")

cambia("        tahona: estado.tahona, encargosFecha: estado.encargosFecha",
       "        tahona: estado.tahona, encargosFecha: estado.encargosFecha,\n"
       "        cascadas: estado.cascadas",
       "el estado las devuelve")

# ---------------------------------------------------------------- 2 · los endpoints
cambia("    /* -------- encargos: lo que hay que tener un día y hay que pedir antes */",
       """    /* -------- las cascadas: una tarea que, al hacerse, hace nacer la siguiente */
    const limpiaTarea = (x) => String(x || '')
      .toLowerCase()
      .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
      .replace(/\\s+/g, ' ').trim().slice(0, 120);

    /* solo coordinación y la Jefa montan cascadas */
    const puedeCascada = (quien) => /^(co|ge)/.test(String(quien || ''));

    if (ruta.endsWith('/cascada') && metodo === 'POST') {
      if (!cuerpo || !puedeCascada(cuerpo.quien)) {
        return { status: 403, body: { ok: false, error: 'solo coordinación y la Jefa' } };
      }
      const tarea = limpiaTarea(cuerpo.tarea);
      if (!tarea) return { status: 400, body: { ok: false, error: 'falta la tarea' } };
      const hijos = (Array.isArray(cuerpo.hijos) ? cuerpo.hijos : [])
        .map(h => ({
          que: String((h && h.que) || '').trim().slice(0, 200),
          p: ['tienda', 'coordinacion', 'gerencia'].includes(h && h.p) ? h.p : 'tienda',
          turno: ['manana', 'tarde'].includes(h && h.turno) ? h.turno : null,
          cuando: Number.isFinite(Number(h && h.cuando)) ? Math.max(0, Math.min(30, Number(h.cuando))) : 0
        }))
        .filter(h => h.que);
      const estado = await leer();
      if (!estado.cascadas) estado.cascadas = {};
      if (!hijos.length) delete estado.cascadas[tarea];
      else estado.cascadas[tarea] = hijos;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, cascadas: podado.cascadas } };
    }

    /* lanzar la cascada: se llama al terminar una tarea */
    if (ruta.endsWith('/cascada-lanzar') && metodo === 'POST') {
      const tarea = limpiaTarea(cuerpo && cuerpo.tarea);
      const fecha = String((cuerpo && cuerpo.fecha) || '');
      if (!tarea || !/^\\d{4}-\\d{2}-\\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'faltan datos' } };
      }
      const estado = await leer();
      const hijos = (estado.cascadas && estado.cascadas[tarea]) || [];
      if (!hijos.length) return { status: 200, body: { ok: true, nacidos: [] } };

      const hoy = hoyISO(zona);
      const creados = [];
      for (const h of hijos) {
        /* la fecha del hijo: nunca en el pasado */
        let f = fecha;
        if (h.cuando > 0) {
          const d = new Date(fecha + 'T12:00:00Z');
          d.setUTCDate(d.getUTCDate() + h.cuando);
          f = d.toISOString().slice(0, 10);
        }
        if (f < hoy) f = hoy;
        /* si ya está puesto para ese día, no se duplica */
        const clave = 'cascada:' + tarea + ':' + limpiaTarea(h.que) + ':' + f;
        const ya = (estado.encargos || []).some(x =>
          x.clave === clave && !x.hecho);
        if (ya) continue;
        const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        estado.encargos.push({
          id: id, t: h.que, p: h.p, f: f, turno: h.turno,
          diario: false, tipo: 'extra', clave: clave,
          deCascada: tarea, q: marca, h: hora, hecho: false
        });
        creados.push({ id: id, t: h.que, p: h.p, f: f, turno: h.turno });
      }
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, nacidos: creados, encargos: podado.encargos } };
    }

    /* -------- encargos: lo que hay que tener un día y hay que pedir antes */""",
       "los dos endpoints de las cascadas")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
